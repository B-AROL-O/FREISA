import logging
from typing import Optional

import httpx


class LLMClient:
    """Manages communication with the LLM provider (OpenWebUI)."""

    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: Optional[str] = None,
        *,
        chat_endpoint: str = "/api/chat/completions",
        models_endpoint: str = "/api/models",
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.chat_endpoint = chat_endpoint
        self.models_endpoint = models_endpoint
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def test_connection(self):
        """Test connection by performing GET request at models endpoint"""
        url = f"{self.base_url}{self.models_endpoint}"
        response = httpx.get(url, headers=self.headers, timeout=10.0)
        response.raise_for_status()
        if self.model not in [x for n in response.json()["data"] for x in [n.id, n.name]]:
            raise ValueError(f"Requested model {self.model} not found!")

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
                response = await client.post(url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except httpx.RequestError as e:
            error_message = f"Error getting LLM response: {str(e)}"
            logging.error(error_message)

            if isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
                logging.error(f"Status code: {status_code}")
                logging.error(f"Response details: {e.response.text}")

            return f"I encountered an error: {error_message}. Please try again or rephrase your request."
