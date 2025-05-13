from utils.logger_util import LoggerUtil
from utils.google_cloud_util import GoogleCloudUtil
from utils.project_values import *

from utils.env_loader import *
from Step_4.src.pdf_downloader import PDFDownloader


# Define relevant table constants
DRUG_INFO_INFRA_TABLE = f"{INFRA}_{DRUG_INFO_TABLE_ID}"
DRUG_INFO_FULL_TABLE_ID = f"{PROJECT_ID}.{BIG_QUERY_DATASET_ID}.{DRUG_INFO_INFRA_TABLE}"
DRUG_NAMES_QUERY = f"SELECT DISTINCT brand_name FROM `{DRUG_INFO_FULL_TABLE_ID}`"

# Define constants for logging
LOGS_TABLE_NAME = "drug_pdfs_ingestion_logs"
LOGS_FULL_TABLE_ID = f"{PROJECT_ID}.{BIG_QUERY_DATASET_ID}.{INFRA}_{LOGS_TABLE_NAME}"
LOG_FILENAME = "my_logs.log"

# Define GCP bucket that will contain the pdf files
BUCKET_INFRA_FOLDER_PATH = f"{DRUG_PDFS_FOLDER_PATH}/{INFRA}_{DRUG_PDFS_FOLDER_NAME}"

# Init helper classes
gcloud_util = GoogleCloudUtil(JSON_CREDS_TEMPLATE, gcloud_creds_dict)
logger_util = LoggerUtil(LOG_FILENAME)
pdf_downloader = PDFDownloader(logger_util, gcloud_util)

# Get list of drug names
logger_util.log_info("Program start...")
drug_names = pdf_downloader.query_for_drug_names(DRUG_NAMES_QUERY)

# Filter out the drug names that already have corresponding pdf files in GCP bucket
logger_util.log_info(f"Creating list of drugs that don't have pdf files already...")
drug_names_without_pdfs = pdf_downloader.create_list_of_drugs_without_pdfs_in_google_cloud(DRUG_PDFS_BUCKET_NAME, BUCKET_INFRA_FOLDER_PATH, drug_names)
logger_util.log_info(f"Obtained {len(drug_names)} drug names from {DRUG_INFO_FULL_TABLE_ID}")

# Make GET request to get a drug's webpage from dailymed
PREPEND_URL = 'https://dailymed.nlm.nih.gov'
logger_util.log_info(f"Getting page urls per drug name; count: {len(drug_names)}")
drug_name_and_page_links = pdf_downloader.get_page_url_for_each_drug_name(PREPEND_URL, drug_names_without_pdfs)

# Get the pdf link for each drug 
logger_util.log_info(f"Getting pdf links per drug name; count: {len(drug_name_and_page_links)}")
drug_name_and_pdf_links = pdf_downloader.get_pdf_link_for_each_drug_name(PREPEND_URL, drug_name_and_page_links)

# Create GCP bucket (if it doesnt already exist)
logger_util.log_info(f"Getting pdfs and uploading to Google Bucket: {BUCKET_INFRA_FOLDER_PATH}; count: {len(drug_name_and_pdf_links)}")
gcloud_util.ensure_create_bucket(DRUG_PDFS_BUCKET_NAME)

# Make GET request for a drug's pdf file and then upload it to GCP bucket
pdf_downloader.for_each_drug_get_pdf_and_upload_to_bucket(drug_name_and_pdf_links, DRUG_PDFS_BUCKET_NAME, BUCKET_INFRA_FOLDER_PATH)

# Upload logs to Big Query
logger_util.log_info(f"Uploading log file: {LOG_FILENAME} to Big Query table: {LOGS_FULL_TABLE_ID}")
logs_df = logger_util.get_log_file_content_as_dataframe()
logger_util.log_info(f"-- Program DONE -- ")
gcloud_util.upsert_dataframe_to_big_query(logs_df,[], LOGS_FULL_TABLE_ID)