from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_groq import ChatGroq
# from langchain_openai import ChatOpenAI
from backend.config import get_settings

settings = get_settings()

def get_llm():
    """Returns the configured LLM instance."""
    if settings.LLM_PROVIDER == "gemini":
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0,
            convert_system_message_to_human=True
        )
    
    # Placeholder for other providers
    # elif settings.LLM_PROVIDER == "groq":
    #     return ChatGroq(...)
    
    else:
        raise ValueError(f"Unsupported LLM Provider: {settings.LLM_PROVIDER}")
