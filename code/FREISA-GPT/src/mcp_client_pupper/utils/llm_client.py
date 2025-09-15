import json
import logging
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class LLMClientConfig:
    model: str
    base_url: str
    api_key: Optional[str]
    chat_endpoint: str = "/api/chat/completions"
    models_endpoint: str = "/api/models"


class LLMClient:
    """Manages communication with the LLM provider (OpenWebUI)."""

    def __init__(self, config: LLMClientConfig):
        self.model = config.model
        self.base_url = config.base_url.rstrip("/")
        self.chat_endpoint = config.chat_endpoint
        self.models_endpoint = config.models_endpoint
        self.api_key = config.api_key
        self.headers = (
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            if self.api_key is not None
            else {
                "Content-Type": "application/json",
            }
        )

    def test_connection(self) -> bool:
        """Test connection by performing GET request at models endpoint"""
        url = f"{self.base_url}{self.models_endpoint}"
        try:
            response = httpx.get(url, headers=self.headers, timeout=10.0)
            response.raise_for_status()
        except httpx.RequestError as e:
            logger.error(f"Error reaching LLM models endpoint: {str(e)}")
            return False

        if self.model not in [x for n in response.json()["data"] for x in [n["id"], n["name"]]]:
            logger.error(f"Requested model {self.model} not found!")
            return False

        return True

    async def get_response(self, messages: list[dict[str, str]]) -> str:
        """Get a response from the LLM.

        Args:
            messages: A list of message dictionaries ().

        Returns:
            The LLM's response as a string.

        Raises:
            httpx.RequestError: If the request to the LLM fails.
        """
        url = f"{self.base_url}{self.chat_endpoint}"

        payload = {
            "messages": messages,
            "model": self.model,
            "temperature": 0.7,
            "max_tokens": 4096,
            "top_p": 1,
            "stream": False,
            "stop": None,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self.headers, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                logger.debug(data)
                return json.dumps(data["choices"][0]["message"])

        except httpx.RequestError as e:
            error_message = f"Error getting LLM response: {str(e)}"
            logger.error(error_message)

            if isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
                logger.error(f"Status code: {status_code}")
                logger.error(f"Response details: {e.response.text}")

            return f"I encountered an error: {error_message}. Please try again or rephrase your request."
