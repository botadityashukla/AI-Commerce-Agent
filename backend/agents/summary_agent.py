from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.core.llm import get_llm
from backend.core.logger import setup_logger

logger = setup_logger(__name__)

SUMMARY_PROMPT = """Summarize the following conversation for a support agent handoff.
Include the key issue, any solutions provided, and the customer's sentiment.

Conversation History:
{history}
"""

def summary_agent_node(state: Dict[str, Any]):
    """
    Node for summarizing the conversation.
    """
    logger.info("Entering Summary Agent Node")
    messages = state.get("messages", [])
    
    # Format history as string
    # Assuming messages is a list of objects or dicts with 'content'
    history_str = "\n".join([f"{msg.type if hasattr(msg, 'type') else 'user/ai'}: {msg.content}" for msg in messages])
    
    llm = get_llm()
    chain = ChatPromptTemplate.from_template(SUMMARY_PROMPT) | llm | StrOutputParser()
    
    summary = chain.invoke({"history": history_str})
    
    logger.info("Conversation summarized", extra={"payload": {"summary": summary}})
    
    return {"messages": [f"System Note: {summary}"], "agent_used": "SummaryAgent"}
