from unittest.mock import MagicMock, patch
from io import BytesIO
import json

import pytest
from Step_5.src.llm_summarizer import LLMSummarizer



@pytest.fixture
def expected_text():
    return "It's a twap!!"

@pytest.fixture
def mock_bedrock_util(expected_text):    
    mock_response_body = {
        "content": [{"text": expected_text}]
    }

    # Correct: serialize only real strings/data
    mock_response = {
        'body': BytesIO(json.dumps(mock_response_body).encode('utf-8'))
    }

    mock_bedrock_util = MagicMock()
    mock_bedrock_util.bedrock_client.invoke_model.return_value = mock_response
    return mock_bedrock_util

@pytest.fixture
def llm_summarizer(mock_bedrock_util) -> dict[str, str]:        
    mock_logger_util = MagicMock()
    mock_gcloud_util = MagicMock()            
    mock_aws_props = {"model_id": "foo-val", "accept": "foo-accept", "content_type": "foo-content-type"}
    my_instance = LLMSummarizer(mock_logger_util, mock_gcloud_util, mock_bedrock_util, mock_aws_props)
    return my_instance


def test_call_bedrock_api_returns_properly(llm_summarizer, mock_bedrock_util, expected_text):     
    payload = {"input": "Hello"}
    res = llm_summarizer._call_bedrock_api(payload_body=payload)
    assert res == expected_text 


def test_call_bedrock_api_calls_bedrock_once(llm_summarizer, mock_bedrock_util):     
    payload = {"input": "Hello"}
    llm_summarizer._call_bedrock_api(payload_body=payload)
    mock_bedrock_util.bedrock_client.invoke_model.assert_called_once()