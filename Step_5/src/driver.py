import os
import json
from typing import Dict

from utils.env_loader import *
from utils.project_values import *
from utils.logger_util import LoggerUtil
from utils.google_cloud_util import GoogleCloudUtil
from utils.bedrock_util import BedrockUtil
from Step_5.src.llm_summarizer import LLMSummarizer


LOG_FILENAME = "my_logs.log"
AWS_SECRETS_NAME = "AWS_SECRETS_AI_PROJECT"
BUCKET_INFRA_FOLDER_PATH = f"{DRUG_PDFS_FOLDER_PATH}/{INFRA}_{DRUG_PDFS_FOLDER_NAME}"
DRUG_SUMMARIES_INFRA_TABLE = f"{INFRA}_{DRUG_SUMMARIES_TABLE_ID}"
DRUG_SUMMARIES_FULL_TABLE_ID = f"{PROJECT_ID}.{BIG_QUERY_DATASET_ID}.{DRUG_SUMMARIES_INFRA_TABLE}"

def _get_aws_credentials(gcloud_util: GoogleCloudUtil, project_number: str, secret_name: str) -> Dict[str, str]:
    access_key_id = gcloud_util.get_secret(project_number, secret_name)
    assert access_key_id  
    aws_creds_dict = json.loads(access_key_id)    
    return aws_creds_dict

# Init helper classes
gcloud_util = GoogleCloudUtil(JSON_CREDS_TEMPLATE, gcloud_creds_dict)
logger_util = LoggerUtil(LOG_FILENAME)
logger_util.log_info(f"Retrieving AWS secrets named: {AWS_SECRETS_NAME}")
aws_creds = _get_aws_credentials(gcloud_util, PROJECT_ID, AWS_SECRETS_NAME)
bedrock_util = BedrockUtil(aws_creds)
llm_summarizer = LLMSummarizer(logger_util, gcloud_util, bedrock_util, LLM_AWS_PROPS)


logger_util.log_info("Program start...")
pdf_blobs = llm_summarizer.get_list_of_pdf_blobs_from_bucket(DRUG_PDFS_BUCKET_NAME, BUCKET_INFRA_FOLDER_PATH)
logger_util.log_info(f"PDF blobs retrieved: {len(pdf_blobs)}")

logger_util.log_info("Filtering out blobs that already have an entry on Big Query Table")
filtered_pdf_blobs = llm_summarizer.filter_out_blobs_with_existing_entries(pdf_blobs, DRUG_SUMMARIES_FULL_TABLE_ID)
logger_util.log_info(f"Blobs left after filtering: {len(filtered_pdf_blobs)}") 

logger_util.log_info("Getting drug summary for each PDF blob...")
drug_summaries = llm_summarizer.chunkified_get_drug_summary_for_each_brand_name(10, filtered_pdf_blobs, LLM_CLASSIFICATION_TEMPLATE, DRUG_SUMMARIES_FULL_TABLE_ID)
                                                         
LOGS_TABLE_NAME = "drug_summaries_logs"
LOGS_FULL_TABLE_ID = f"{PROJECT_ID}.{BIG_QUERY_DATASET_ID}.{INFRA}_{LOGS_TABLE_NAME}"
logger_util.log_info(f"Uploading log file: {LOG_FILENAME} to Big Query table: {LOGS_FULL_TABLE_ID}")
logs_df = logger_util.get_log_file_content_as_dataframe()
logger_util.log_info(f"-- Program complete --")
gcloud_util.upsert_dataframe_to_big_query(logs_df,[], LOGS_FULL_TABLE_ID)