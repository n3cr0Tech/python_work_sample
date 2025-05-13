import requests
import pandas as pd
from pandas import DataFrame
from google.cloud import bigquery
import time
import os
from datetime import datetime
from typing import Dict, List
import json

# for GoogleCloudUtil
from google.cloud import storage, bigquery, secretmanager
from google.cloud.bigquery import SchemaField
from google.oauth2 import service_account
from google.auth.credentials import Credentials
from google.cloud.exceptions import NotFound

class GoogleCloudUtil:
    def __init__(self, _json_creds_template: str, _gcloud_credentials_dict: Dict[str, str]):                
        self.json_creds_template_obj = json.loads(_json_creds_template)
        self.gcloud_credentials = None
        self.bigquery_client = None
        self.storage_client = None
        self.secret_mgr_client = None
        self._ensure_get_gcloud_credentials(self.json_creds_template_obj, _gcloud_credentials_dict)        
        self._ensure_create_big_query_client(self.gcloud_credentials)
        self._ensure_create_storage_client(self.gcloud_credentials)
        self._ensure_create_secret_manager_client(self.gcloud_credentials)

    # =============================== Secret Manager ===============================
    def get_secret(self, project_number: str, secret_id: str, version: str = "latest") -> str | None:
        full_secret_name =  f"projects/{project_number}/secrets/{secret_id}/versions/{version}"
        secret_val = None
        try:
            # Access the secret version
            encoded_secret = self.secret_mgr_client.access_secret_version(name=full_secret_name)
            # Get the payload data (the secret value)
            secret_val = encoded_secret.payload.data.decode("UTF-8")        
        except Exception as e:
            print(f"Error retrieving secret: {e}")
        return secret_val        


    # =============================== BUCKETS ===============================
    def get_bucket(self, bucket_name:str) -> storage.Bucket:
        bucket_obj =None
        try:
            bucket_obj = self.storage_client.get_bucket(bucket_name)
        except Exception as e:
            print(f"Error in getting bucket: {bucket_name}")
        return bucket_obj

    # file_path example: "some_folder/possibly_another_folder/filenname.file_ext"
    #NOTE: file_path DOES NOT need bucket_name prepended to it
    def file_exists_in_gcloud_bucket(self, bucket_name, bucket_file_path: str) -> bool:
        bucket_obj = self.storage_client.bucket(bucket_name)
        blob = bucket_obj.blob(bucket_file_path)
        return blob.exists()

    def ensure_create_bucket(self, bucket_name: str) -> storage.Bucket:
        buck_obj = self.storage_client.lookup_bucket(bucket_name)
        if buck_obj is None:
            buck_obj = self._create_bucket(bucket_name)        
        return buck_obj

    def _create_bucket(self, bucket_name: str) -> storage.Bucket:
        try:
            bucket = self.storage_client.create_bucket(bucket_name)
            print(f"Bucket {bucket_name} created.")
        except Exception as e:
            print(f"Error in creating bucket: {bucket_name}")
        return bucket

    def create_folders_in_bucket(self, bucket_name: str, folder_names: List[str]):
        try:
            # Create folders in the bucket (folders are simulated by prefixing object names)
            bucket = self.storage_client.get_bucket(bucket_name)
            for folder in folder_names:
                # The folder is just an object with a "folder name" as a prefix and a trailing slash.
                folder_blob = bucket.blob(folder + '/')
                folder_blob.upload_from_string('')  # Uploading an empty string
                print(f"Folder '{folder}' created in bucket {bucket_name}.")
        except Exception as e:
            print(f"Error in creating folders for bucket: {bucket_name}")


    # bucket_blob_filepath example: "util_modules/your-file.pdf"
    # destination_filepath example: "./your-file.pdf" 
    def download_file_from_gcloud_bucket(self, bucket_name, bucket_blob_filepath, destination_filepath):    
        try:                        
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(bucket_blob_filepath)
              # Check if the blob exists
            if not blob.exists():
                print(f"Error: The file {bucket_blob_filepath} does not exist in the bucket.")            
            else:
                blob.download_to_filename(destination_filepath)
                print(f"File {bucket_blob_filepath} downloaded to {destination_filepath}")
        except Exception as e:
            print(f"Error: {e}")        

    def upload_file_to_gcloud(self, bucket_name: str, gcloud_filepath: str, local__filepath: str):                
        bucket = self.storage_client.bucket(bucket_name=bucket_name)
        blob = bucket.blob(gcloud_filepath)
        try:
            blob.upload_from_filename(local__filepath)
        except Exception as e:
            print(f"Error with GCloud upload: {e}")

    # Returns True if successful, False if failed
    def upload_string_as_pdf_into_bucket(self, bucket_name: str, gcloud_filepath: str, content: str) -> bool:
        bucket = self.storage_client.bucket(bucket_name=bucket_name)
        blob = bucket.blob(gcloud_filepath)
        is_successful = True
        try:
            blob.upload_from_string(content, content_type="application/pdf")
        except Exception as e:
            print(f"Error with GCloud upload: {e}")
            is_successful = False
        return is_successful

    # =============================== Big Query ===============================
    # returns 0 if table is not found
    def get_total_row_count_of_table(self, full_table_id) -> int:
        total_row_count = 0
        table_obj = self.bigquery_client.get_table(full_table_id)
        if table_obj:
            total_row_count = table_obj.num_rows
        return total_row_count

    # full_table_id format is PROJECT_ID.DATASET_ID.TABLE_ID
    def get_query_from_biq_query(self, query: str) -> DataFrame | None:
        result = None
        print(query)
        try:
            query_job = self.bigquery_client.query(query=query)
            result = query_job.result().to_dataframe()
        except Exception as e:
            print(f"ERROR in get_query_from_big_query()   {e}")
        return result

    def get_query_by_batch(self, query: str, batch_size: int, offset: int) -> DataFrame|None:
        batch_res = None
        query += f"LIMIT {batch_size} OFFSET {offset}" # append LIMIT and OFFSET to original query
        job_config = self._batch_job_config(batch_size, offset)    
        try:
            query_job = self.bigquery_client.query(query, job_config=job_config)
            results = query_job.result()
            batch_res = results.to_dataframe()
        except Exception as e:
            print(f"ERROR in get_query_by_batch... {e}")
        return batch_res

    # returns the number of rows removed from table
    def remove_duplicates_from_table(self, full_table_id) -> int:
        query = f"""
            CREATE OR REPLACE TABLE {full_table_id} AS 
            SELECT DISTINCT *  
            FROM {full_table_id}
        """
        original_row_count = self.get_total_row_count_of_table(full_table_id)
        self.get_query_from_biq_query(query)  # remove duplicate rows
        new_row_count = self.get_total_row_count_of_table(full_table_id)
        rows_removed = original_row_count - new_row_count
        return rows_removed
        

    # full_table_id format is PROJECT_ID.DATASET_ID.TABLE_ID
    def upsert_dataframe_to_big_query(self, combined_df: DataFrame, schema: List[SchemaField], full_table_id: str):                
        table = self._ensure_table_exists(full_table_id, self.bigquery_client, schema)
        autodetect_schema = self._ensure_autodetect_schema(schema)
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND, #append data to bigquery table
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,  # Adjust this if your CSV has a header row
            autodetect=autodetect_schema,  # Do not auto-detect schema
            schema=schema  # Use the defined schema
        )
        self._upload_data_to_big_query(combined_df, job_config, full_table_id)
    
    def replace_table_with_new_data_on_big_query(self, df: DataFrame, schema: List[SchemaField], full_table_id: str):
        self.ensure_delete_existing_table(full_table_id)
        autodetect_schema = self._ensure_autodetect_schema(schema)
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, #append data to bigquery table
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,  # Adjust this if your CSV has a header row
            autodetect=autodetect_schema,  # Do not auto-detect schema
            schema=schema  # Use the defined schema
        )    
        self._upload_data_to_big_query(df, job_config, full_table_id)

    def delete_table(self, full_table_id: str):
        table_ref = self.bigquery_client.get_table(full_table_id)   
        try:    
            self.bigquery_client.delete_table(table_ref)
        except Exception as e:
            print(f"ERROR deleting table {full_table_id}... {e}")

    def _upload_data_to_big_query(self, df: DataFrame, job_config: bigquery.job.LoadJobConfig, full_table_id: str):
        load_job = self.bigquery_client.load_table_from_dataframe(df, full_table_id, job_config)
        load_job.result()  # Waits for the job to complete
        print(f"Loaded {len(df)} rows into {full_table_id}")


    def ensure_delete_existing_table(self, full_table_id: str):
        if self.table_exists(full_table_id):
            self.delete_table(full_table_id)        

    def table_exists(self, full_table_id:str) -> bool:
        res = False
        try:
            # Try to fetch the table
            table = self.bigquery_client.get_table(full_table_id)
            res = True            
        except NotFound:            
            print(f"Table: {full_table_id} does NOT exist")
        return res
    
    def _batch_job_config(self, batch_size: int, cur_row: int) -> bigquery.QueryJobConfig:
        return bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("batch_size", "INT64", batch_size),
                bigquery.ScalarQueryParameter("start_row", "INT64", cur_row),
            ]
        )    

    def _ensure_autodetect_schema(self, schema: List[SchemaField]) -> bool:
        autodetect_schema = False
        if len(schema) == 0:
            autodetect_schema = True 
        return autodetect_schema

    def _ensure_create_secret_manager_client(self, _gcloud_credentials_dict: Dict[str, str]):
        if self.secret_mgr_client is None:
            self.secret_mgr_client = secretmanager.SecretManagerServiceClient(credentials=_gcloud_credentials_dict)
        return self.secret_mgr_client
    
    def _ensure_create_storage_client(self, _gcloud_credentials_dict: Dict[str, str]):
        if self.storage_client is None:
            self.storage_client = storage.Client(credentials=_gcloud_credentials_dict)
        return self.storage_client

    def _ensure_create_big_query_client(self, _gcloud_credentials_dict: Dict[str, str]):
        if self.bigquery_client is None:            
            self.bigquery_client = bigquery.Client(credentials=_gcloud_credentials_dict)
        return self.bigquery_client  

    def _ensure_table_exists(self, full_table_id: str, bigquery_client: bigquery.Client, schema: List[Dict[str, str]]) -> bigquery.table.Table:
        table = None
        if self.table_exists(full_table_id):
             # Try to fetch the table
            table = bigquery_client.get_table(full_table_id)            
        else:
            # Table doesnt exist so create it
            table = self._create_table(full_table_id, bigquery_client, schema)
        return table

    def _create_table(self, table_ref: str, bigquery_client: bigquery.Client, schema: List[Dict[str, str]]):        
        # Create the table
        table = bigquery.Table(table_ref, schema=schema)
        table = bigquery_client.create_table(table)
        print(f"Created table {table_ref}  {datetime.now()}")
        return table

    def _ensure_get_gcloud_credentials(self, json_creds_template: Dict[str, str], gcloud_creds_dict: Dict[str, str]) -> Credentials:
        if self.gcloud_credentials is None:
            gcloud_json_credentials = self._load_gcloud_credentials(json_creds_template, gcloud_creds_dict)
            self.gcloud_credentials = service_account.Credentials.from_service_account_info(gcloud_json_credentials) 
        return self.gcloud_credentials

    def _load_gcloud_credentials(self, json_template: Dict[str, str], gcloud_creds_dict: Dict[str, str]) -> Dict[str, str]:        
        json_template["project_id"] = gcloud_creds_dict["project_id"]
        json_template["private_key_id"] = gcloud_creds_dict["private_key_id"]
        json_template["private_key"] = gcloud_creds_dict["private_key"].replace("\\n", "\n")        
        json_template["client_email"] = gcloud_creds_dict["client_email"]
        json_template["client_id"] = gcloud_creds_dict["client_id"]
        return json_template