from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.agents.faq_agent import faq_agent_node
from backend.agents.escalation_agent import escalation_agent_node
from backend.agents.summary_agent import summary_agent_node
from backend.core.llm import get_llm
from backend.core.logger import setup_logger

logger = setup_logger(__name__)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    agent_used: str
    ticket: Union[dict, None]

# Router Prompt
ROUTER_PROMPT = """Classify the user's message into one of the following intentions:
- "FAQ": General questions, policy inquiries, how-to questions.
- "ESCALATE": User is angry, frustrated, threatens to leave, or explicitly asks for a human.
- "SUMMARY": User says goodbye, "end chat", or indicates the session is over.

Return JSON: {{"intent": "FAQ" | "ESCALATE" | "SUMMARY"}}

User Message: {message}
"""

def classification_node(state: AgentState):
    """
    Decides the next agent to call based on the user's last message.
    """
    messages = state["messages"]
    user_message = messages[-1].content
    
    llm = get_llm()
    chain = ChatPromptTemplate.from_template(ROUTER_PROMPT) | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({"message": user_message})
        intent = result.get("intent", "FAQ")
    except Exception:
        intent = "FAQ" # Default fallback
        
    logger.info(f"Router classified intent: {intent}")
    return {"decision": intent}

def router_edge(state: AgentState) -> str:
    # This function is used in the conditional edge to pull the decision from the state
    # But wait, LangGraph edges usually look at the state returned by the node.
    # We'll use a slightly different pattern: The classification node returns a dict, 
    # but we need to pass that to the edge.
    
    # Actually, let's make the classification node return the update to a 'decision' key in state?
    # Or just use the router logic directly in the conditional edge function.
    # To keep decision logic traceable, let's keep the classification LLM call separate if possible,
    # but for simplicity in this graph, I'll put the classification logic inside the 'conditional_edge'.
    pass

def route_decision(state: AgentState):
    messages = state["messages"]
    if not messages:
        return "faq"
        
    last_msg = messages[-1]
    if isinstance(last_msg, AIMessage):
        return END
        
    user_message = last_msg.content
    
    llm = get_llm()
    chain = ChatPromptTemplate.from_template(ROUTER_PROMPT) | llm | JsonOutputParser()
    
    try:
        result = chain.invoke({"message": user_message})
        intent = result.get("intent", "FAQ").upper()
    except Exception as e:
        logger.error(f"Routing failed, defaulting to FAQ: {e}")
        intent = "FAQ"
        
    if intent == "ESCALATE":
        return "escalation"
    elif intent == "SUMMARY":
        return "summary"
    else:
        return "faq"

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("faq", faq_agent_node)
builder.add_node("escalation", escalation_agent_node)
builder.add_node("summary", summary_agent_node)

builder.set_conditional_entry_point(
    route_decision,
    {
        "faq": "faq",
        "escalation": "escalation",
        "summary": "summary"
    }
)

builder.add_edge("faq", END)
builder.add_edge("escalation", END)
builder.add_edge("summary", END)

graph = builder.compile()
