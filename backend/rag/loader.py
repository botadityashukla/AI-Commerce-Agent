import os
from typing import List
from langchain_core.documents import Document
from backend.core.logger import setup_logger

logger = setup_logger(__name__)

def load_knowledge_base(file_path: str) -> List[Document]:
    """Loads the knowledge base text file and chunks it."""
    if not os.path.exists(file_path):
        logger.error(f"Knowledge base file not found at: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Simple splitting by double newline to separate sections
        # In a real app, we'd use a RecursiveCharacterTextSplitter
        sections = text.split("\n\n")
        documents = []
        
        for section in sections:
            if section.strip():
                # Use the first line as metadata source/title if possible
                lines = section.strip().split("\n")
                content = section.strip()
                title = lines[0] if lines else "General"
                
                doc = Document(
                    page_content=content,
                    metadata={"source": "knowledge.txt", "title": title}
                )
                documents.append(doc)
                
        logger.info(f"Loaded {len(documents)} documents from knowledge base.", extra={"payload": {"count": len(documents)}})
        return documents

    except Exception as e:
        logger.error(f"Error loading knowledge base: {str(e)}")
        raise e
