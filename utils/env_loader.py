from dotenv import load_dotenv
import os

load_dotenv()

CRONJOB_ID = os.getenv("CRONJOB_ID")
assert CRONJOB_ID is not None

INFRA = os.getenv("INFRA")
PROJECT_ID = os.getenv("PROJECT_ID")
BUCKET_NAME = os.getenv("BUCKET_NAME")
BUCKET_FOLDER = os.getenv("BUCKET_FOLDER")
BUCKET_MODULES_FOLDER = os.getenv("BUCKET_MODULES_FOLDER")
ENV_VARS_MODULE = os.getenv("ENV_VARS_MODULE")
PRIVATE_KEY_ID = os.getenv("PRIVATE_KEY_ID")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CLIENT_EMAIL = os.getenv("CLIENT_EMAIL")
CLIENT_ID = os.getenv("CLIENT_ID")
GCP_SECRETS_PROJECT_NUMBER=os.getenv("GCP_SECRETS_PROJECT_NUMBER")
GCP_AWS_SECRET_ID=os.getenv("GCP_AWS_SECRET_ID")

PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")
SECRET_ID = os.getenv("AWS_SECRET_KEY_ID")


gcloud_creds_dict = {}
gcloud_creds_dict["project_id"] = PROJECT_ID
gcloud_creds_dict["private_key_id"] = PRIVATE_KEY_ID
gcloud_creds_dict["private_key"] = PRIVATE_KEY
gcloud_creds_dict["client_email"] = CLIENT_EMAIL
gcloud_creds_dict["client_id"] = CLIENT_ID
