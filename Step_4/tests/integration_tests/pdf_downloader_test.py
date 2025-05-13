from unittest.mock import MagicMock
import pytest
from utils.env_loader import *
from utils.logger_util import LoggerUtil
from utils.google_cloud_util import GoogleCloudUtil
from utils.project_values import *

from Step_4.src.pdf_downloader import PDFDownloader



@pytest.fixture
def gcloud_util() -> GoogleCloudUtil:
    gcloud_util = GoogleCloudUtil(JSON_CREDS_TEMPLATE, gcloud_creds_dict)
    return gcloud_util




# This test runs the entire driver except for the start where it queries the drug_info table for drug_names
# The main goal of this test is to answer:
# 1. Does the GET requests and soup tag extractions still work with the current website of dailymed?
# 2. Does the Google Bucket and folders exist for the pdfs?
# 3. Does the pdf uploading functionality work properly?
def test_get_drug_pdf_and_upload_to_bucket_is_successful(gcloud_util):
    BUCKET_INFRA_FOLDER_PATH = f"{DRUG_PDFS_FOLDER_PATH}/{INFRA}_{DRUG_PDFS_FOLDER_NAME}"
    MOCK_DRUG_NAMES = ['AVIANE', 'NIMODIPINE', 'DANTROLENE', 'THYROID', 'ESTRACE', 'NADOLOL']
    PREPEND_URL = 'https://dailymed.nlm.nih.gov'
      
    logger_util = LoggerUtil("test.logs")
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)
    logger_util.log_info("Program start...")
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)
    
    logger_util.log_info(f"Getting page urls per drug name; count: {len(MOCK_DRUG_NAMES)}")
    drug_name_and_page_links = pdf_downloader.get_page_url_for_each_drug_name(PREPEND_URL, MOCK_DRUG_NAMES)
    logger_util.log_info(f"Getting pdf links per drug name; count: {len(drug_name_and_page_links)}")
    drug_name_and_pdf_links = pdf_downloader.get_pdf_link_for_each_drug_name(PREPEND_URL, drug_name_and_page_links)
    logger_util.log_info(f"Getting pdfs and uploading to Google Bucket: {MOCK_DRUG_NAMES}; count: {len(drug_name_and_pdf_links)}")
    pdf_downloader.for_each_drug_get_pdf_and_upload_to_bucket(drug_name_and_pdf_links, DRUG_PDFS_BUCKET_NAME, BUCKET_INFRA_FOLDER_PATH)

    #check that all drug's pdfs have been uploaded to Google Buckets
    for drug_name in MOCK_DRUG_NAMES:
        file_name = f"{drug_name}.pdf"
        bucket_path = f"{BUCKET_INFRA_FOLDER_PATH}/{file_name}"        
        file_exists = gcloud_util.file_exists_in_gcloud_bucket(DRUG_PDFS_BUCKET_NAME, bucket_path)
        logger_util.log_debug(f"PDF exists in {bucket_path} for {drug_name} - {file_exists}")
        assert file_exists is True
