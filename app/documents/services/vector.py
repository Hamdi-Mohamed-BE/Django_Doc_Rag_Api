import os

from typing import List, Tuple, Dict, Any

from langchain_community.vectorstores import Chroma
# TODO change to gemeni embedding or ollama (some free embedding)
from langchain_openai import OpenAIEmbeddings

import settings

from documents import models as document_models
from documents import enums as document_enums
from documents.services.parsers import DocumentParser

from langchain_core.documents import Document


CHROMA_PERSIST_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db"
)


class DocumentVectorStore():
    """Concrete implementation of BaseVectorStore for document vectorization."""
    
    def get_retriever(
        self,
    ):
        embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
        )
        vector_store = Chroma(
            collection_name="restaurant_reviews",
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embeddings
        )
        retriever = vector_store.as_retriever(
            search_kwargs={"k": 5}
        )
        return retriever

    @property
    def collection_name(self) -> str:
        """Return the name of the Chroma collection for documents."""
        return "documents"
    
    def _prepare_data_texts(
        self,
        document: document_models.Document,
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """Prepare data texts and metadata for document vectorization."""
    
        texts_and_metadata = []
        document.status = document_enums.DocumentProcessingStatus.PROCESSING
        document.save(
            update_fields=["status", "updated_at"]
        )
        
        if not document.document_file:
            return texts_and_metadata
        
        try:
            metadata = {
                "uid": str(document.uid),
                "title": document.title,
                "description": document.description or "",
                "user_id": str(document.user_id),
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
            }
            parser = DocumentParser(document)
            for text, meta in parser.download_and_parse_document(document):
                metadata.update(meta)
                texts_and_metadata.append((text, metadata))
        
        except Exception as e:
            print(f"Error processing document {document.uid}: {e}")
            document.status = document_enums.DocumentProcessingStatus.FAILED
            document.save(
                update_fields=["status", "updated_at"]
            )
        
        document.status = document_enums.DocumentProcessingStatus.COMPLETED
        document.save(
            update_fields=["status", "updated_at"]
        )
        return texts_and_metadata

    def add_documents(
        self,
        document: document_models.Document,
    ) -> None:
        texts_and_metadata = self._prepare_data_texts(
            document=document
        )
        embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
        )
        vector_store = Chroma(
            collection_name="restaurant_reviews",
            persist_directory=CHROMA_PERSIST_DIR,
            embedding_function=embeddings
        )

        documents = []
        ids = []
        for idx in range(0, len(texts_and_metadata)):
            text = texts_and_metadata[idx][0]
            print("Text:", text)
            metadata = texts_and_metadata[idx][1]
            uid = metadata.get("uid")
            _id = f"{self.collection_name}_{uid}_{idx}"
            document = Document(
                page_content=text,
                metadata=metadata,
                id=_id
            )
            documents.append(document)
            ids.append(_id)
        
        if documents:
            vector_store.add_documents(documents=documents, ids=ids)
