from langchain.schema import Document
import fitz
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_voyageai import VoyageAIEmbeddings
from utils.logger_util import LoggerUtil
from utils.google_cloud_util import GoogleCloudUtil
from utils.ai_drug_env_vars import *


class RetrieverUtil:
    def __init__(self, gcloud_util: GoogleCloudUtil, logger_util: LoggerUtil, voyage_key: str):        
        self.gcloud_util = gcloud_util
        self.logger_util = logger_util                        
        self.embeddings = self._create_embeddings(voyage_key)
        
        PDF_FILES = ["icd10_list.pdf", "read_clinical_pubmed.pdf"] #pdf files to process
        self._download_pdf_files(PDF_FILES)
        self.retriever = self._create_retriever_process(PDF_FILES, self.embeddings)

    def _create_retriever_process(self, pdf_files: list[str], embeddings):
        pdf_docs = [Document(page_content=self._load_pdf_text(f)) for f in pdf_files if os.path.exists(f)]
        assert len(pdf_docs) > 1
        # Split all documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(pdf_docs)

        # Create FAISS vector store
        vector_store = FAISS.from_documents(all_splits, embeddings)
        retriever = vector_store.as_retriever()
        assert retriever is not None
        return retriever

    def _load_pdf_text(self, pdf_path: str):
        """Extracts text from a PDF file and returns it as a string."""
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text("text") + "\n" for page in doc)
        return text.strip()


    def _download_pdf_files(self, pdf_files: list[str]):
        for filename in pdf_files:
            bucket_name = DRUG_PDFS_BUCKET_NAME
            blob_src = f"util_modules/{filename}"
            destination_filename = f"./{filename}"
            self.gcloud_util.download_file_from_gcloud_bucket(bucket_name, blob_src, destination_filename)

    def _create_embeddings(self, voyage_key: str):
        embeddings = None
        try:
            embeddings = VoyageAIEmbeddings(model="voyage-3-lite", api_key=voyage_key)
        except Exception as e:
            self.logger_util.log_error(f"Error creating Voyage embedings: {e}")
        assert embeddings is not None
        return embeddings

