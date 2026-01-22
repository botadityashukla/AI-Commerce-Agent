from typing import Dict, Any
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from backend.core.llm import get_llm
from backend.core.logger import setup_logger

logger = setup_logger(__name__)

# Escalation Prompt (JSON Output)
ESCALATION_SYSTEM_PROMPT = """You are an escalation specialist. 
Analyze the user's complaint and create a structured support ticket.
Return ONLY valid JSON with the following fields:
- issue_summary: A brief title of the problem.
- sentiment: (Angry, Frustrated, Confused)
- priority: (High, Medium, Low)
- response_message: A polite message to the user confirming the ticket creation and apologizing.

User Message: {message}
"""

def escalation_agent_node(state: Dict[str, Any]):
    """
    Node for handling escalated queries.
    Generates a ticket and returns a confirmation.
    """
    logger.info("Entering Escalation Agent Node")
    messages = state.get("messages", [])
    user_message = messages[-1].content if messages else ""
    
    llm = get_llm()
    chain = ChatPromptTemplate.from_template(ESCALATION_SYSTEM_PROMPT) | llm | JsonOutputParser()
    
    try:
        ticket_data = chain.invoke({"message": user_message})
        
        # In a real app, save ticket to DB here
        logger.info("Ticket created", extra={"payload": ticket_data})
        
        # Return the polite acknowledgement from the specific field
        response_text = ticket_data.get("response_message", "I have created a support ticket for you.")
        
        # We append the ticket data to the state for the API to return if needed
        return {
            "messages": [response_text], 
            "ticket": ticket_data,
            "agent_used": "EscalationAgent"
        }
        
    except Exception as e:
        logger.error(f"Escalation failed: {e}")
        return {
            "messages": ["I apologize, but I couldn't create a ticket automatically. Please email support@example.com."],
            "agent_used": "EscalationAgent"
        }
