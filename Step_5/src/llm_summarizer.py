import json
import botocore
from botocore.exceptions import NoCredentialsError, ClientError
import pandas as pd 
import json
from datetime import datetime, timezone
import pandas as pd
from google.cloud import storage
from typing import Dict, List
import PyPDF2
import io

from Step_5.src.drug_summary_model import DrugSummary
from utils.project_values import *
from utils.logger_util import LoggerUtil
from utils.google_cloud_util import GoogleCloudUtil



class LLMSummarizer():
    def __init__(self,  logger_util: LoggerUtil, gcloud_util: GoogleCloudUtil, bedrock_util, aws_props: Dict[str, str]):
        self.logger_util = logger_util
        self.gcloud_util = gcloud_util
        # Initialize Bedrock API client
        self.bedrock_util = bedrock_util
        self._init_aws_variables(aws_props)        
        
    def _init_aws_variables(self, aws_props: Dict[str, str]):
        self.model_id = aws_props['model_id']
        self.accept = aws_props["accept"]
        self.content_type = aws_props["content_type"]

    def ensure_upload_drug_summaries_to_big_query(self, drug_summaries: List[Dict[str, str]], schema: List[Dict[str, str]], full_table_id: str):
        if drug_summaries and len(drug_summaries) > 0:
            df_drug_summaries = pd.DataFrame(drug_summaries)
            self.gcloud_util.upsert_dataframe_to_big_query(df_drug_summaries, schema, full_table_id)
            self.logger_util.log_info(f"Drug summaries uploaded to Big Query: {full_table_id}")
        else:
            self.logger_util.log_info(f"No drug summaries to upload")

    def chunkified_get_drug_summary_for_each_brand_name(self, chunk_size: int, pdf_blobs: List[storage.Blob], classification_template: str, DRUG_SUMMARIES_FULL_TABLE_ID: str):        
        drug_summaries = []
        for i in range(0, len(pdf_blobs)):  
            pdf_blob = pdf_blobs[i]
            brand_name = self._extract_brand_name_from_pdf_blob(pdf_blob.name)
            self.logger_util.log_debug(f"Getting summary for {brand_name}")            
            drug_summary = self._ensure_get_classification_for_pdf(pdf_blob, classification_template)   
            drug_summaries = self._ensure_append_drug_summary(brand_name, drug_summaries, drug_summary)        
            for_loop_is_complete = i == len(pdf_blobs) - 1    
            drug_summaries = self._ensure_upload_chunk_and_reset_drug_summaries_list(for_loop_is_complete, chunk_size, drug_summaries, DRUG_SUMMARIES_FULL_TABLE_ID)


    def _ensure_upload_chunk_and_reset_drug_summaries_list(self, for_loop_is_complete: bool, chunk_size: int, drug_summaries: List[DrugSummary], DRUG_SUMMARIES_FULL_TABLE_ID: str) -> List[Dict[str, any]]:
        result = drug_summaries
        if len(drug_summaries) == chunk_size or for_loop_is_complete:
            self.logger_util.log_info(f"Uploading {len(drug_summaries)} drug summaries to {DRUG_SUMMARIES_FULL_TABLE_ID}")
            self.ensure_upload_drug_summaries_to_big_query(drug_summaries, LLM_DRUG_SUMMARIES_SCHEMA, DRUG_SUMMARIES_FULL_TABLE_ID)
            result = []
        return result
    
    def _ensure_append_drug_summary(self, brand_name: str, drug_summaries: List[Dict[str, any]], classification_res: str | None) -> List[Dict[str, any]]:
        if classification_res is None:
            self.logger_util.log_info(f"Failed to get classification result for {brand_name}")
        else:
            drug_summary = DrugSummary(brand_name=brand_name, summary=classification_res)
            drug_summary.extract_categories()
            new_entry = {
                'brand_name': drug_summary.brand_name,
                'summary': drug_summary.summary,
                **drug_summary.as_response()
            }
            drug_summaries.append(new_entry)
        return drug_summaries

    # example of bucket_path = "drug_model/data/drug_pdfs"
    def get_list_of_pdf_blobs_from_bucket(self, bucket_name:str, bucket_path: str) -> List[storage.Blob]:
        pdf_blobs = []
        try:
            bucket_obj = self.gcloud_util.get_bucket(bucket_name)
            assert bucket_obj is not None
            blobs = list(bucket_obj.list_blobs(prefix=bucket_path))            
            # get the filenames from bucket blobs
            pdf_blobs = [blob for blob in blobs if blob.name.endswith('.pdf')]            
        except Exception as e:
            self.logger_util.log_error(f"Failed to get list of filenames from bucket: {e}")
        return pdf_blobs

    def filter_out_blobs_with_existing_entries(self, pdf_blobs: List[storage.Blob], drug_summary_full_table_id: str) -> List[storage.Blob]:
        result = []
        big_query_existing_entries = self._ensure_get_existing_brand_names_from_drug_summaries(drug_summary_full_table_id)
        for pdf_blob in pdf_blobs:
            result = self._ensure_append_blob_if_no_existing_entry(pdf_blob, big_query_existing_entries, result)
        return result
    
    def _ensure_get_existing_brand_names_from_drug_summaries(self, full_table_id: str) -> List[str]:
        result = []
        if self.gcloud_util.table_exists(full_table_id):    
            query = f"""SELECT DISTINCT brand_name FROM {full_table_id}"""
            self.logger_util.log_info(f"Getting distinct brand names from {full_table_id}")
            df_result = self.gcloud_util.get_query_from_biq_query(query)
            result = df_result['brand_name'].to_list()
        return result

    def _ensure_append_blob_if_no_existing_entry(self, pdf_blob: storage.Blob, existing_entries: List[str], result: List[storage.Blob]) -> List[storage.Blob]:        
        brand_name = self._extract_brand_name_from_pdf_blob(pdf_blob.name)
        if brand_name not in existing_entries:
            result.append(pdf_blob)
        return result

    def _call_bedrock_api(self, payload_body: Dict[str, str]) -> str:
        """Call Bedrock API with the extracted text for text generation."""        
        body = json.dumps(payload_body)
        result = None
        try:
            response = self.bedrock_util.bedrock_client.invoke_model(body=body, modelId=self.model_id, accept=self.accept, contentType=self.content_type)
            response_body = json.loads(response.get('body').read())
            result = response_body["content"][0]["text"]
        except (NoCredentialsError, ClientError) as e:
            self.logger_util.log_error(f"Error calling Bedrock API: {e}")
        return result

    def _predict_classification(self, text: str, classification_template: str) -> str:
        """Insert the extracted text into the prompt and predict classification using Bedrock API."""
        # Format the prompt by inserting the text into the prompt template
        formatted_prompt = classification_template.format(text=text)
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": formatted_prompt}]
                }
            ],
        }
        # Call the Bedrock API with the formatted prompt
        return self._call_bedrock_api(body)

    def _get_pdf_text_from_blob(self, pdf_blob: storage.Blob) -> str:
        """Extract text from the PDF blob content."""
        pdf_content = pdf_blob.download_as_bytes()
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text_data = ''

        # Extract text from the first 10 pages
        for page_num in range(min(20, len(reader.pages))):
            page = reader.pages[page_num]
            text_data += page.extract_text()

        return text_data
    
    def _extract_brand_name_from_pdf_blob(self, pdf_filename: str) -> str:
        return pdf_filename.split('/')[-1].replace('.pdf', '')

    def _ensure_get_classification_for_pdf(self, pdf_blob: storage.Blob, classification_template: str) -> str | None:
        classification_result = None
        try:
            text_data = self._get_pdf_text_from_blob(pdf_blob)
            self.logger_util.log_debug(f"Calling _predict_classification on {pdf_blob.name}")
            classification_result = self._predict_classification(text_data, classification_template)
        except Exception as e:
            self.logger_util.log_error(f"Failed to get classificattion on brand name: {pdf_blob.name}, error: {e}")
        return classification_result