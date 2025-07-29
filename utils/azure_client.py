import os
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI

class AzureOpenAIClient:
    """Azure OpenAI client wrapper"""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not self.api_key or not self.endpoint:
            raise ValueError("Azure OpenAI credentials not configured. Please set AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT environment variables.")
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
    
    def chat_completion(self, 
                       model: str,
                       messages: List[Dict[str, str]],
                       max_tokens: int = 1000,
                       temperature: float = 0.1,
                       response_format: Optional[Dict[str, str]] = None) -> Any:
        """Create chat completion using Azure OpenAI"""
        
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            if response_format:
                kwargs["response_format"] = response_format
            
            response = self.client.chat.completions.create(**kwargs)
            return response
            
        except Exception as e:
            raise Exception(f"Azure OpenAI chat completion failed: {str(e)}")
    
    def validate_connection(self) -> bool:
        """Validate Azure OpenAI connection"""
        
        try:
            response = self.chat_completion(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            return True
            
        except Exception as e:
            print(f"Azure OpenAI connection validation failed: {str(e)}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
            
        except Exception as e:
            print(f"Failed to get available models: {str(e)}")
            return []
