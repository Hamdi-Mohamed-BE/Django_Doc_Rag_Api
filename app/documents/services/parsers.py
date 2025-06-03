import os
import requests

from langchain_community import document_loaders
from documents import models as document_models

import settings


TEMP_FILE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp_files"
)
if not os.path.exists(TEMP_FILE_DIR):
    os.makedirs(TEMP_FILE_DIR)
    print(f"Created temporary file directory: {TEMP_FILE_DIR}")


class DocumentParser:
    PARSERS_TYPE_MAP = {
        "pdf": document_loaders.PyMuPDFLoader,
        "txt": document_loaders.TextLoader,
        "docx": document_loaders.Docx2txtLoader,
        "csv": document_loaders.CSVLoader,
        "json": document_loaders.JSONLoader,
    }
    
    def __init__(self, document: document_models.Document):
        """Initialize the parser with a document instance."""
        self.document = document
        self.file_path = None
        self.file_extension = None

    @classmethod
    def get_parser(cls, file_extension: str):
        """Get the appropriate parser class based on the file extension."""
        parser_class = cls.PARSERS_TYPE_MAP.get(file_extension.lower())
        if not parser_class:
            raise ValueError(f"No parser available for file type: {file_extension}")
        return parser_class
    
    def get_file_url(self, file_field) -> str:
        if settings.DEFAULT_FILE_STORAGE == "django.core.files.storage.FileSystemStorage":
            return f"{settings.BACKEND_URL}{file_field.url}"
        return file_field.url

    def parse_document(self) -> list:
        """Parse the document using the appropriate parser."""
        parser_class = self.get_parser(self.file_extension)
        loader = parser_class(self.file_path)
        
        for item in loader.lazy_load():
            yield item.page_content, item.metadata
   
    def download_and_parse_document(self, document: document_models.Document) -> list:
        """Download the document file and parse it."""
        self.file_extension = document.document_file.name.split('.')[-1]
        self.file_path = os.path.join(TEMP_FILE_DIR, f"{document.uid}.{self.file_extension}")
        with open(self.file_path, 'wb') as file:
            file.write(requests.get(self.get_file_url(document.document_file)).content)
            print(f"Downloaded document to {self.file_path}")
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Temporary file {self.file_path} not found.")
        return self.parse_document()
        
    def __del__(self):
        """Clean up resources when the instance is deleted."""
        if not self.file_path:
            return
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
            print(f"Temporary file {self.file_path} deleted.")