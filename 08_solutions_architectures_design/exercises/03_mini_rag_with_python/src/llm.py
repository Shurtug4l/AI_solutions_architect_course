from openai import OpenAI
from typing import List, Dict, Any, Generator

class LLMClient:
    def __init__(self, base_url: str = "http://localhost:1234/v1", api_key: str = "lm-studio"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Generator:
        try:
            stream = self.client.chat.completions.create(
                model="mistralai/ministral-3-3b",
                messages=messages,
                temperature=temperature,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        try:
            response = self.client.chat.completions.create(
                model="mistralai/ministral-3-3b",
                messages=messages,
                temperature=temperature,
                stream=False
            )
            # Handle possible None response or errors
            if response and response.choices:
                return response.choices[0].message.content or ""
            return ""
        except Exception as e:
            return f"Error: {str(e)}"
