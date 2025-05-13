import json
from typing import Dict
# from langchain_aws import ChatBedrock
import boto3
import botocore


class BedrockUtil():
    def __init__(self, aws_credentials: Dict[str, str]):
        self.model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
        self.accept = 'application/json'
        self.content_type = 'application/json'    
        self.bedrock_client = None
        self._ensure_bedrock_client(aws_credentials)        


    # Deprecated since various steps manipulate the LLM result differently
    # returns string if SUCCESSFUL,
    # otherwiser, returns None
    # def invoke_model(self, body: str) -> str | None:
    #     result = None
    #     try:
    #        response = self.bedrock_client.invoke_model(body=body, model_id=self.model_id, accept=self.accept, contentType=self.content_type)
    #        response_body = json.loads(response.get('body').read())
    #        result = response_body["content"][0]["text"]
    #     except Exception as e:
    #         print(f"Error invoke_model: {e}")        
    #     return result
    

    def _ensure_bedrock_client(self, aws_credentials: Dict[str, str]) -> botocore.client.BaseClient:
        if self.bedrock_client is None:
            self.bedrock_client = self._create_bedrock_client(aws_credentials)
        return self.bedrock_client
    
    def _create_bedrock_client(self, aws_credentials: Dict[str, str]) -> botocore.client.BaseClient:
        # Initialize the boto3 client for Amazon Bedrock with explicit credentials
        client = boto3.client(
            "bedrock-runtime", 
            region_name=aws_credentials["AWS_DEFAULT_REGION"],
            aws_access_key_id=aws_credentials["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=aws_credentials["AWS_SECRET_ACCESS_KEY"]
        )
        return client