from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.rag.vector_store import vector_store
from backend.core.llm import get_llm
from backend.core.logger import setup_logger

logger = setup_logger(__name__)

# FAQ Prompt
FAQ_SYSTEM_PROMPT = """You are a helpful customer support AI for a company. 
Use the following context to answer the user's question. 
If the answer is not in the context, say you don't know and suggest asking for a human agent.
Keep answers concise and polite.

Context:
{context}
"""

faq_prompt = ChatPromptTemplate.from_messages([
    ("system", FAQ_SYSTEM_PROMPT),
    ("user", "{question}")
])

def faq_agent_node(state: Dict[str, Any]):
    """
    Node for handling FAQ queries using RAG.
    Expects state to have 'messages' and a recent user message.
    """
    logger.info("Entering FAQ Agent Node")
    messages = state.get("messages", [])
    user_message = messages[-1].content if messages else ""
    
    # 1. Retrieve Knowledge
    docs = vector_store.similarity_search(user_message, k=3)
    context = "\n\n".join([d.page_content for d in docs])
    
    # 2. Generate Answer
    llm = get_llm()
    chain = faq_prompt | llm | StrOutputParser()
    
    response = chain.invoke({"context": context, "question": user_message})
    
    logger.info("FAQ Agent generated response", extra={"payload": {"response": response, "context_docs": len(docs)}})
    
    return {"messages": [response], "agent_used": "FAQAgent"}
