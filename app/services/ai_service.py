"""AI service for OpenRouter integration."""

from urllib import response

import httpx
import uuid

from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import text

from app.config.settings import settings
from app.db.models.schemas import ChatRequest, ChatResponse, ModelInfo
from app.core.logging import get_logger
from app.core.security import mask_api_key

logger = get_logger(__name__)


class AIService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self):
        """Initialize the AI service."""

        # Cliente para OpenRouter
        self.openrouter_client = httpx.AsyncClient(
            base_url=settings.openrouter_base_url,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
                # "HTTP-Referer": "https://github.com/your-username/template-python-fastapi",
                "X-Title": settings.app_name,
            },
            timeout=30.0,
        )

        # Cliente para Gemma (Ollama local)
        self.gemma_client = httpx.AsyncClient(
            base_url=settings.gemma_url,    
            headers={
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

        logger.info(
            f"AI Service initialized with API key: {mask_api_key(settings.openrouter_api_key)}"
        )
        
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        print("Request received in AIService:", request)
        try:
            return await self._openrouter_completion(request)

        except Exception as e:
            logger.warning("OpenRouter failed, switching to Gemma")
            return await self._gemma_completion(request)
        
        
    

    async def _openrouter_completion(self, request):

        response = await self.openrouter_client.post(
            "/chat/completions",
            json=request
        )

        data = response.json()

        if "choices" not in data:
            print("OpenRouter error:", data)
            raise Exception("OpenRouter response error")

        return data["choices"][0]["message"]["content"]
    
    async def _gemma_completion(self, request: ChatRequest):

        prompt = request.messages[-1].content

        response = await self.gemma_client.post(
            "/generate",
            json={
                "model": "gemma3:4b",
                "prompt": prompt,
                "stream": False
            }
        )

        response.raise_for_status()

        data = response.json()

        return ChatResponse(
            id=str(uuid.uuid4()),
            created=int(datetime.now().timestamp()),
            model="gemma3:4b",
            choices=[
                {
                    "message": {
                        "role": "assistant",
                        "content": data.get("response", "")
                    }
                }
            ],
            usage=None
    )
        
    async def list_models(self) -> List[ModelInfo]:
        """List available models from OpenRouter."""
        try:
            logger.info("Fetching available models from OpenRouter")
            response = await self.openrouter_client.get("/models")
            response.raise_for_status()
            
            data = response.json()
            models_data = data.get("data", [])
            
            models = [
                ModelInfo(
                    id=model.get("id", ""),
                    name=model.get("name"),
                    description=model.get("description"),
                    pricing=model.get("pricing")
                )
                for model in models_data
            ]
            
            logger.info(f"Retrieved {len(models)} models")
            return models
            
        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Error fetching models: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def health_check(self) -> bool:
        """Check if the AI service is healthy."""
        try:
            # Try to fetch models as a simple health check
            await self.list_models()
            return True
        except Exception as e:
            logger.error(f"AI service health check failed: {str(e)}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.openrouter_client.aclose()
        await self.gemma_client.aclose()
        logger.info("AI service client closed")

    async def simple_prompt(self, prompt: str):

        request = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        return await self._openrouter_completion(request)

# Global AI service instance
ai_service = AIService()
