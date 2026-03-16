from typing import Optional, Dict, List
from langchain_ollama import OllamaLLM
from loguru import logger
import os
from dotenv import load_dotenv
import json
import re

load_dotenv("config/.env")

class OllamaLLMService:
    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        temperature: float = 0.1,
        max_tokens: int = 1000
    ):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.temperature = temperature
        self.max_tokens = max_tokens

        logger.info(f"Initializing ollama LLM (model:{self.model})")

        self.llm = OllamaLLM(
            model = self.model,
            base_url = self.base_url,
            temperature = self.temperature,
            max_tokens = self.max_tokens
        )

        self._test_connection()

    def _test_connection(self):
        try:
            response = self.llm.invoke("Hello")
            logger.info(f"Ollama LLM connected (reponse: {len(response)} chars)")
        except Exception as e:
            logger.error(f"Ollama LLM connection failed: {e}")
            raise

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        if temperature is not None or max_tokens is not None:
            temp_llm = OllamaLLM(
                model = self.model,
                base_url = self.base_url,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )

            response = temp_llm.invoke(prompt)
        else:
            response = self.llm.invoke(prompt)
        
        return response
    
    def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        retry_delay: int = 5,
        **kwargs
    ):
        for attempt in range(max_retries):
            try:
                response = self.generate(prompt, **kwargs)
                return response
            
            except Exception as e:
                logger.warning(f"Generation attempt {attempt+1} failed: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} attempts failed")
                    raise
                
                # Wait before retry
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception("Generation failed after all retries")

        
if __name__ == "__main__":
    service = OllamaLLMService()
    
    # Test simple generation
    prompt = "What is diabetes in one sentence?"
    response = service.generate(prompt)
    
    print("="*70)
    print("LLM SERVICE TEST")
    print("="*70)
    print(f"\nPrompt: {prompt}")
    print(f"Response: {response}")
    
    # Test with different temperature
    creative_prompt = "Explain diabetes using a cooking metaphor."
    creative_response = service.generate(creative_prompt, temperature=0.7)
    
    print(f"\n\nCreative Prompt: {creative_prompt}")
    print(f"Response: {creative_response}")
    
    # Test retry
    print("\n\nTesting retry mechanism...")
    try:
        retry_response = service.generate_with_retry("Test query", max_retries=2)
        print(f"✅ Retry successful: {retry_response[:50]}...")
    except Exception as e:
        print(f"❌ Retry failed: {e}")