"""
LEXGUARD AI — Groq API Wrapper
Provides a Gemini-compatible `GenerativeModel` interface for Groq models (Llama, Mixtral).
"""

import json
from groq import AsyncGroq

class MockUsageMetadata:
    def __init__(self, prompt_tokens: int, completion_tokens: int):
        self.prompt_token_count = prompt_tokens
        self.candidates_token_count = completion_tokens

class MockGenerateContentResponse:
    def __init__(self, text: str, prompt_tokens: int, completion_tokens: int):
        self.text = text
        self.usage_metadata = MockUsageMetadata(prompt_tokens, completion_tokens)

class GroqModelWrapper:
    """
    A wrapper around AsyncGroq that exposes the same interface as
    google.generativeai.GenerativeModel.
    """
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.client = AsyncGroq(api_key=api_key, max_retries=5)

    async def generate_content_async(self, prompt: str, generation_config=None) -> MockGenerateContentResponse:
        temperature = getattr(generation_config, "temperature", 0.7) if generation_config else 0.7
        max_tokens = getattr(generation_config, "max_output_tokens", 8192) if generation_config else 8192

        # Convert the prompt into Groq Chat format
        messages = [
            {"role": "user", "content": prompt}
        ]

        # Call Groq API
        chat_completion = await self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            temperature=temperature,
            max_completion_tokens=max_tokens,
        )

        response_text = chat_completion.choices[0].message.content
        
        # In case the model returns markdown JSON blocks and we need raw JSON
        if getattr(generation_config, "response_mime_type", None) == "application/json":
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

        usage = chat_completion.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0

        return MockGenerateContentResponse(
            text=response_text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens
        )
