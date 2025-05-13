import json
from typing import Dict
from unittest.mock import MagicMock

import PyPDF2
import pytest
from Step_5.src.llm_summarizer import LLMSummarizer
from Step_5.src.drug_summary_model import DrugSummary
from utils.bedrock_util import BedrockUtil
from utils.env_loader import *
from utils.project_values import *
from utils.logger_util import LoggerUtil
from utils.google_cloud_util import GoogleCloudUtil

from google.cloud import storage
import os

class PDF_Helper:
    def __init__(self):
       pass

    def get_sample_data_path(self, file_name: str) -> str:
        cur_dir = os.getcwd()
        file_name += ".pdf"
        filepath= os.path.join(cur_dir, "Step_5\sample_data", file_name)
        return filepath        

    def get_sample_pdf_content(self, file_path: str) -> str:
        with open(file_path, "rb") as file:
            # Initialize the PDF reader
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            # Iterate through all the pages and extract text
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

        return text

@pytest.fixture
def pdf_helper() -> PDF_Helper:
    return PDF_Helper()

@pytest.fixture
def gcloud_util() -> GoogleCloudUtil:
    gcloud_util = GoogleCloudUtil(JSON_CREDS_TEMPLATE, gcloud_creds_dict)
    return gcloud_util

@pytest.fixture
def aws_credentials(gcloud_util: GoogleCloudUtil) -> dict[str, str]:        
    access_key_id = gcloud_util.get_secret(GCP_SECRETS_PROJECT_NUMBER, GCP_AWS_SECRET_ID)
    assert access_key_id  
    aws_creds_dict = json.loads(access_key_id)    
    return aws_creds_dict

@pytest.fixture
def bedrock_util(aws_credentials):
    bedrock_util = BedrockUtil(aws_credentials)
    return bedrock_util

def test_call_bedrock_api_returns_properly_and_drug_summary_has_expected_fields(pdf_helper, gcloud_util, bedrock_util):
    BRAND_NAME = "ABREVA"            
    LOCAL_PDF_PATH = pdf_helper.get_sample_data_path(BRAND_NAME)
    logger_util = MagicMock()
    llm_summarizer = LLMSummarizer(logger_util, gcloud_util, bedrock_util, LLM_AWS_PROPS)
    sample_pdf_text = pdf_helper.get_sample_pdf_content(LOCAL_PDF_PATH)

    actual = llm_summarizer._predict_classification(sample_pdf_text, LLM_CLASSIFICATION_TEMPLATE)
    assert actual is not None

    drug_summary = DrugSummary(brand_name=BRAND_NAME, summary=actual)
    drug_summary.extract_categories()    
    assert "This product may cause a severe allergic reaction" in drug_summary.warnings_precautions
    assert "boxed_warning" in drug_summary.adverse_reactions_library_of_medicine
    assert len(drug_summary.boxed_warning) > 0