
from unittest.mock import patch, MagicMock

from utils.google_cloud_util import GoogleCloudUtil
from Step_4.src.pdf_downloader import PDFDownloader

def test_ensure_get_url_from_tag_handles_missing_href():
    logger_util = MagicMock()
    gcloud_util = MagicMock()    
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)
    mock_tag_missing_href = {"some_attr": "123"}
    actual = pdf_downloader._ensure_get_url_from_tag(mock_tag_missing_href)
    assert actual is None

def test_ensure_append_to_dict_if_not_none_returns_properly():
    logger_util = MagicMock()
    gcloud_util = MagicMock()
    mock_drug_name = "yacapsul"
    mock_tag_link ="foo_tag"
    mock_base_url = 'https://dailymed.nlm.nih.gov'
    expected = {}
    expected[mock_drug_name] = mock_base_url + mock_tag_link
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)
    actual = pdf_downloader._ensure_append_to_dict_if_not_none({}, mock_drug_name, mock_base_url, mock_tag_link)
    assert actual == expected

def test_ensure_append_to_dict_if_not_none_returns_empty_dict_when_tag_link_is_None():
    logger_util = MagicMock()
    gcloud_util = MagicMock()
    mock_drug_name = "yacapsul"    
    mock_base_url = 'https://dailymed.nlm.nih.gov'
    expected = {}
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)
    actual = pdf_downloader._ensure_append_to_dict_if_not_none({}, mock_drug_name, mock_base_url, None)
    assert actual == expected

def test_get_page_url_for_each_drug_name_calls_functions_N_times():
    logger_util = MagicMock()
    gcloud_util = MagicMock()
    mock_drug_names = ["tylenol", "yacapsul", "chemicalX", "NZT"]    
    mock_get_response = MagicMock()
    mock_get_response.text = "foo-blah"
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)
    with patch.object(pdf_downloader, '_ensure_get_url_from_tag', return_value=mock_get_response) as mock_ensure_get_url, \
        patch.object(pdf_downloader, '_send_get_request') as mock_send_get_req, \
        patch.object(pdf_downloader, '_ensure_append_to_dict_if_not_none') as mock_ensure_append, \
        patch.object(pdf_downloader, '_soup_extract_tag') as mock_soup_extract:
        pdf_downloader.get_page_url_for_each_drug_name('foo-url', mock_drug_names)
        assert mock_ensure_get_url.call_count == len(mock_drug_names)
        assert mock_send_get_req.call_count == len(mock_drug_names)
        assert mock_soup_extract.call_count == len(mock_drug_names)
        assert mock_ensure_append.call_count == len(mock_drug_names)
    

def test_get_page_url_for_each_drug_name_excludes_drugs_with_no_links_found():
    logger_util = MagicMock()
    gcloud_util = MagicMock()
    mock_drug_names = ["tylenol"]    
    mock_get_response = MagicMock()
    mock_get_response.text = "foo-blah"
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)
    expected = {}
    with patch.object(pdf_downloader, '_ensure_get_url_from_tag') as mock_ensure_get_url, \
        patch.object(pdf_downloader, '_send_get_request') as mock_send_get_req, \
        patch.object(pdf_downloader, '_ensure_append_to_dict_if_not_none', return_value={}) as mock_ensure_append, \
        patch.object(pdf_downloader, '_soup_extract_tag') as mock_soup_extract:
        actual = pdf_downloader.get_page_url_for_each_drug_name('foo-url', mock_drug_names)
        assert actual == expected


def test_get_pdf_link_for_each_drug_name_calls_functions_N_times():
    logger_util = MagicMock()
    gcloud_util = MagicMock()
    mock_drug_page_links = {"tylenol": "foo-page-link", "NZT": "foo-page-link"}   
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)
    mock_get_response = MagicMock()
    mock_get_response.text = "foo-drug-page-text"
    with patch.object(pdf_downloader, '_ensure_append_to_dict_if_not_none') as mock_ensure_append, \
        patch.object(pdf_downloader, '_ensure_get_url_from_tag') as mock_ensure_get_url, \
        patch.object(pdf_downloader, '_send_get_request', return_value=mock_get_response) as mock_send_get_req, \
        patch.object(pdf_downloader, '_soup_extract_tag') as mock_soup_extract:
        pdf_downloader.get_pdf_link_for_each_drug_name("foo-prepend-url", mock_drug_page_links)
        assert mock_send_get_req.call_count == len(mock_drug_page_links)
        assert mock_soup_extract.call_count == len(mock_drug_page_links)
        assert mock_ensure_get_url.call_count == len(mock_drug_page_links)
        assert mock_ensure_append.call_count == len(mock_drug_page_links)

def test_create_list_of_drugs_without_pdfs_returns_nothing_when_pdf_exists():
    logger_util = MagicMock()
    gcloud_util = MagicMock()
    mock_drug_names = ["tylenol", "yacapsul", "chemicalX", "NZT"]
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)
    with patch.object(gcloud_util, 'file_exists_in_gcloud_bucket', return_value=True) as mock_file_exists:
        actual = pdf_downloader.create_list_of_drugs_without_pdfs_in_google_cloud("foo-bucket", "blah-bucket-folder", mock_drug_names)
        assert len(actual) == 0

def test_create_list_of_drugs_without_pdfs_calls_functions_N_times():
    logger_util = MagicMock()
    gcloud_util = MagicMock()
    mock_drug_names = ["tylenol", "yacapsul", "chemicalX", "NZT"]
    pdf_downloader = PDFDownloader(logger_util, gcloud_util)

    with patch.object(pdf_downloader, '_ensure_append_drug_name_if_no_pdf_yet') as mock_ensure_append, \
        patch.object(gcloud_util, 'file_exists_in_gcloud_bucket') as mock_file_exists:
        pdf_downloader.create_list_of_drugs_without_pdfs_in_google_cloud("foo-bucket", "blah-bucket-folder", mock_drug_names)        
        assert mock_file_exists.call_count == len(mock_drug_names)
        assert mock_ensure_append.call_count == len(mock_drug_names)
    