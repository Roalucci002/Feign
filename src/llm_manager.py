import requests
import logging
from typing import Optional
import json

logger = logging.getLogger(__name__)

class LLMManager:
    """Ollama LLM インターフェース"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model
        self.available = False
        self._check_connection()
    
    def _check_connection(self) -> bool:
        """Ollama への接続確認"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            self.available = response.status_code == 200
            if self.available:
                logger.info("✓ Connected to Ollama")
            else:
                logger.warning("✗ Could not connect to Ollama")
            return self.available
        except Exception as e:
            logger.error(f"Ollama connection error: {e}")
            self.available = False
            return False
    
    def generate(self, prompt: str, system: str = "", temperature: float = 0.7,
                 top_p: float = 0.9, context_length: int = 4096) -> Optional[str]:
        """テキスト生成"""
        if not self.available:
            logger.error("LLM is not available")
            return None
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_ctx": context_length
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"LLM error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
    
    def list_models(self) -> list:
        """利用可能なモデルを取得"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m.get('name') for m in models]
            return []
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

llm_manager = LLMManager()
