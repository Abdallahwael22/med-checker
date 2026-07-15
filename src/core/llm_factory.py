import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv()

class LLMFactory:
    """
    Factory pattern for creating LLM instances.
    Centralizes configuration and instantiation of models.
    """
    
    @staticmethod
    def get_llm(model: str = "llama-3.3-70b-versatile", temperature: float = 0.0) -> ChatGroq:
        """
        Creates and returns a ChatGroq LLM instance.
        
        Args:
            model (str): The Groq model to use. Defaults to "llama-3.3-70b-versatile".
            temperature (float): The sampling temperature.
            
        Returns:
            ChatGroq: Configured LangChain chat model.
            
        Raises:
            ValueError: If GROQ_API_KEY is not set in the environment.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")
            
        return ChatGroq(
            model=model,
            temperature=temperature,
            api_key=api_key
        )
