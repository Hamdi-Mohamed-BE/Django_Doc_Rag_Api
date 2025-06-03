
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from documents.services.vector import DocumentVectorStore
from documents import models as document_models
from documents import enums as document_enums

import settings


model = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=settings.GOOGLE_API_KEY,
)

template = """
You are an exeprt in answering questions about a document content

Here are some relevant text related to the question:
{context}

Here is the question to answer: {question}
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model


def answer_question(question: str, document: document_models.Document) -> str:
    """
    Answer a question using the LLM chain with the provided question and context.

    Args:
        question (str): The question to answer.

    Returns:
        str: The answer to the question.
    """
    if not document.status == document_enums.DocumentProcessingStatus.COMPLETED:
        DocumentVectorStore().add_documents(
            document
        )
    
    retriever = DocumentVectorStore().get_retriever()

    response = chain.invoke({
        "question": question,
        "context": retriever.invoke(question)
    })
    return response.content if response else "No answer found."