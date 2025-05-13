import re
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas
from pandas import DataFrame
from typing import Dict, Hashable, List
import requests

from utils.logger_util import LoggerUtil
from utils.google_cloud_util import GoogleCloudUtil


class PDFDownloader:
    def __init__(self, logger_util: LoggerUtil, gcloud_util: GoogleCloudUtil):
        self.logger_util = logger_util
        self.gcloud_util = gcloud_util

    def for_each_drug_get_pdf_and_upload_to_bucket(self, drug_names_and_pdf_links: Dict[str, str], bucket_name: str, bucket_path: str):
        for drug_name, pdf_url in drug_names_and_pdf_links.items():
            self.logger_util.log_debug(f"requesting pdf for {drug_name} for url: {pdf_url}")
            response = self._send_get_request(drug_name, pdf_url)
            bucket_file_path = f"{bucket_path}/{drug_name}.pdf"
            self.logger_util.log_debug(f"Calling ensure upload to bucket for {drug_name}")
            self._ensure_upload_pdf_to_bucket(response, bucket_name, bucket_file_path)

    def _ensure_upload_pdf_to_bucket(self, response, bucket_name: str, bucket_file_path: str):
        try: 
            self.logger_util.log_debug(f"Uploading pdf to {bucket_file_path}")
            succeeeded = self.gcloud_util.upload_string_as_pdf_into_bucket(bucket_name, bucket_file_path, response.content)
            self.logger_util.log_debug(f"file uploaded succeeded: {succeeeded}")
        except Exception as e:
            self.logger_util.log_error(f"Failed to upload pdf content: {e}")

    def query_for_drug_names(self, query: str) -> List[str]:
        self.logger_util.log_info(f"Querying Big Query for drug names...")
        # Run the query and get drug names
        self.logger_util.log_info(f"query: {query}")
        drug_names_df = self.gcloud_util.get_query_from_biq_query(query)
        drug_names_df['brand_name'] = drug_names_df['brand_name'].str.upper().str.replace(r'\s+', ' ', regex=True).str.strip().str.replace('/', ' ')
        drugs_list = self._filter_out_nan(drug_names_df)
        return drugs_list
    
    def _filter_out_nan(self, df_drugs: DataFrame) -> List[str]:
        drug_names = df_drugs.brand_name.dropna().unique().tolist() # removes pd.NaN, ensures unique entries ONLY
        filtered_drug_names = [x for x in drug_names if x != "nan"]
        return filtered_drug_names
                
    def create_list_of_drugs_without_pdfs_in_google_cloud(self, bucket_name: str, bucket_folder_path: str, drug_names: List[str]) -> List[str]:
        result = []
        for drug_name in drug_names:
            file_name = f"{drug_name}.pdf"
            file_path = f"{bucket_folder_path}/{file_name}"                                
            drug_already_has_pdf = self.gcloud_util.file_exists_in_gcloud_bucket(bucket_name, file_path)                             
            result = self._ensure_append_drug_name_if_no_pdf_yet(result, drug_name, drug_already_has_pdf)            
        return result
        
    def _ensure_append_drug_name_if_no_pdf_yet(self, drug_names_to_process: List[str], drug_name: str, drug_already_has_pdf: bool) -> List[str]:
        if not drug_already_has_pdf:
            drug_names_to_process.append(drug_name)
        return drug_names_to_process

    # example return: { "DrugA": "www.blah-drugA.pdf", ...}
    def get_pdf_link_for_each_drug_name(self, prepend_url: str, drug_name_and_urls: Dict[str, str]) -> Dict[str, str]:        
        result = {}
        for drug_name, drug_url in drug_name_and_urls.items():
            drug_page_res = self._send_get_request(drug_name, drug_url)
            regex_pattern = r'getFile\.cfm\?setid=.*&type=pdf'
            pdf_link_tag = self._soup_extract_tag(drug_page_res.text, regex_pattern)
            self.logger_util.log_debug(f"drug link tag: {pdf_link_tag}")
            pdf_link = self._ensure_get_url_from_tag(pdf_link_tag)      
            self.logger_util.log_debug(f"drug link: {pdf_link}")      
            result = self._ensure_append_to_dict_if_not_none(result, drug_name, prepend_url, pdf_link)
        return result

    # example return: { "DrugA": "drug page url", ...}
    def get_page_url_for_each_drug_name(self, prepend_url: str, drug_names: List[str]) -> Dict[str, str]:
        result = {}
        search_url = 'https://dailymed.nlm.nih.gov/dailymed/search.cfm'   
        
        for drug_name in drug_names:
            params = {
                'labeltype': 'all',
                'query': drug_name
            } 
            drug_page_res = self._send_get_request(drug_name, search_url, params)                        
            regex_pattern = f'/dailymed/drugInfo.cfm\?setid=.*'
            drug_link_tag = self._soup_extract_tag(drug_page_res.text, regex_pattern)
            self.logger_util.log_debug(f"drug link tag: {drug_link_tag}")
            drug_link = self._ensure_get_url_from_tag(drug_link_tag)            
            self.logger_util.log_debug(f"drug link: {drug_link}")
            self._ensure_append_to_dict_if_not_none(result, drug_name, prepend_url, drug_link)                        
        return result
    
    def _ensure_get_url_from_tag(self, link_tag: Tag) -> str | None:
        link_url = None
        if link_tag and link_tag.get('href') is not None:            
            link_url = link_tag['href']
        return link_url
        
    def _soup_extract_tag(self, html_response_text: str, regex_pattern: str) -> Tag:
        soup = BeautifulSoup(html_response_text, 'html.parser')
        tag = soup.find('a', href=re.compile(regex_pattern))
        return tag

    #by default, request params will be an empty dict
    def _send_get_request(self, drug_name: str, url: str, params: Dict[str, str]={}) -> requests.models.Response:
        try:
            self.logger_util.log_debug(f"GET REQUEST FOR: {url}, params: {params}")
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()                    
        except (ConnectionError, TimeoutError) as e:
            self.logger_util.log_error(f'Skipping {drug_name} due to connection error: {e}')        
        except requests.RequestException as e:            
            self.logger_util.log_error(f'Failed to retrieve PDF URL for {drug_name}: {e}')            
        return res

    def _ensure_append_to_dict_if_not_none(self, some_dict: Dict[str, str], drug_name: str, base_url: str, tag_link: str | None) -> Dict[str, str]:
        if tag_link:
            some_dict[drug_name] = base_url + tag_link
        else:
            self.logger_util.log_info(f"{drug_name} was excluded from process - no link was found")
        return some_dict    
