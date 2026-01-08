"""
Azure OpenAI Integration

Responsibilities:
• Provide a robust wrapper around Azure OpenAI API
• Handle authentication, retries, and error handling
• Support both chat completions and streaming
• Implement rate limiting and token tracking
• Enable function calling for structured outputs

Architecture Decision:
- Encapsulates all OpenAI-specific logic in one place
- Uses exponential backoff for transient failures
- Tracks token usage for cost monitoring
- Supports async operations for better performance
- Validates responses to prevent downstream errors
"""

import asyncio
from typing import List, Dict, Any, Optional, AsyncIterator
from openai import AsyncAzureOpenAI, AzureOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import time

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class AzureOpenAIError(Exception):
    """Base exception for Azure OpenAI integration errors."""
    pass


class AzureOpenAIRateLimitError(AzureOpenAIError):
    """Raised when rate limit is exceeded."""
    pass


class AzureOpenAITimeoutError(AzureOpenAIError):
    """Raised when request times out."""
    pass


class AzureOpenAIClient:
    """
    Production-ready Azure OpenAI client with enterprise features.
    
    Features:
    - Automatic retry with exponential backoff
    - Token usage tracking
    - Request/response logging
    - Streaming support
    - Function calling support
    - Async operations
    
    Example:
        client = AzureOpenAIClient()
        response = await client.chat_completion(
            messages=[{"role": "user", "content": "Hello"}]
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        """
        Initialize Azure OpenAI client.
        
        Args:
            api_key: Azure OpenAI API key (defaults to settings)
            endpoint: Azure OpenAI endpoint URL (defaults to settings)
            deployment: Model deployment name (defaults to settings)
            api_version: API version (defaults to settings)
        """
        self.api_key = api_key or settings.AZURE_OPENAI_API_KEY
        self.endpoint = endpoint or settings.AZURE_OPENAI_ENDPOINT
        self.deployment = deployment or settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self.api_version = api_version or settings.AZURE_OPENAI_API_VERSION
        
        # Initialize async client
        self.async_client = AsyncAzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            timeout=settings.AZURE_OPENAI_TIMEOUT,
            max_retries=0,  # We handle retries manually with tenacity
        )
        
        # Initialize sync client for non-async contexts
        self.sync_client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            timeout=settings.AZURE_OPENAI_TIMEOUT,
            max_retries=0,
        )
        
        logger.info(
            f"Initialized Azure OpenAI client",
            extra={
                "deployment": self.deployment,
                "api_version": self.api_version,
            }
        )
    
    @retry(
        stop=stop_after_attempt(settings.AZURE_OPENAI_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((AzureOpenAIRateLimitError, AzureOpenAITimeoutError)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = 1.0,
        frequency_penalty: Optional[float] = 0.0,
        presence_penalty: Optional[float] = 0.0,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[str] = None,
        **kwargs: Any,
    ) -> ChatCompletion:
        """
        Generate chat completion using Azure OpenAI.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2 to 2)
            presence_penalty: Presence penalty (-2 to 2)
            functions: Function definitions for function calling
            function_call: Control function calling behavior
            **kwargs: Additional OpenAI parameters
        
        Returns:
            ChatCompletion response object
        
        Raises:
            AzureOpenAIError: On API errors after retries exhausted
        """
        start_time = time.time()
        
        temperature = temperature if temperature is not None else settings.AZURE_OPENAI_TEMPERATURE
        max_tokens = max_tokens or settings.AZURE_OPENAI_MAX_TOKENS
        
        try:
            logger.debug(
                f"Sending chat completion request",
                extra={
                    "deployment": self.deployment,
                    "message_count": len(messages),
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
            )
            
            response = await self.async_client.chat.completions.create(
                model=self.deployment,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                functions=functions,  # type: ignore
                function_call=function_call,  # type: ignore
                **kwargs,
            )
            
            duration = time.time() - start_time
            
            # Log successful completion
            logger.info(
                f"Chat completion successful",
                extra={
                    "deployment": self.deployment,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "duration_seconds": round(duration, 2),
                    "finish_reason": response.choices[0].finish_reason if response.choices else None,
                }
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Chat completion failed: {str(e)}",
                extra={
                    "deployment": self.deployment,
                    "duration_seconds": round(duration, 2),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            
            # Convert to our custom exceptions
            if "rate_limit" in str(e).lower():
                raise AzureOpenAIRateLimitError(f"Rate limit exceeded: {str(e)}") from e
            elif "timeout" in str(e).lower():
                raise AzureOpenAITimeoutError(f"Request timeout: {str(e)}") from e
            else:
                raise AzureOpenAIError(f"Azure OpenAI error: {str(e)}") from e
    
    async def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatCompletionChunk]:
        """
        Generate streaming chat completion.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters
        
        Yields:
            ChatCompletionChunk objects as they arrive
        
        Example:
            async for chunk in client.chat_completion_stream(messages):
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="")
        """
        temperature = temperature if temperature is not None else settings.AZURE_OPENAI_TEMPERATURE
        max_tokens = max_tokens or settings.AZURE_OPENAI_MAX_TOKENS
        
        try:
            stream = await self.async_client.chat.completions.create(
                model=self.deployment,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs,
            )
            
            async for chunk in stream:
                yield chunk
                
        except Exception as e:
            logger.error(f"Streaming completion failed: {str(e)}", exc_info=True)
            raise AzureOpenAIError(f"Streaming error: {str(e)}") from e
    
    def extract_content(self, response: ChatCompletion) -> str:
        """
        Extract text content from completion response.
        
        Args:
            response: ChatCompletion response
        
        Returns:
            Extracted text content
        """
        if not response.choices:
            logger.warning("Response has no choices")
            return ""
        
        message = response.choices[0].message
        return message.content or ""
    
    def extract_function_call(self, response: ChatCompletion) -> Optional[Dict[str, Any]]:
        """
        Extract function call from completion response.
        
        Args:
            response: ChatCompletion response
        
        Returns:
            Function call dictionary or None
        """
        if not response.choices:
            return None
        
        message = response.choices[0].message
        if hasattr(message, "function_call") and message.function_call:
            return {
                "name": message.function_call.name,
                "arguments": message.function_call.arguments,
            }
        return None
    
    def get_token_count(self, response: ChatCompletion) -> Dict[str, int]:
        """
        Extract token usage from response.
        
        Args:
            response: ChatCompletion response
        
        Returns:
            Dictionary with prompt_tokens, completion_tokens, total_tokens
        """
        if response.usage:
            return {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
    
    async def close(self) -> None:
        """Close the client connections."""
        await self.async_client.close()
        self.sync_client.close()


# Global client instance
_client: Optional[AzureOpenAIClient] = None


def get_openai_client() -> AzureOpenAIClient:
    """
    Get or create global Azure OpenAI client instance.
    
    Returns:
        Shared AzureOpenAIClient instance
    """
    global _client
    if _client is None:
        _client = AzureOpenAIClient()
    return _client


async def simple_chat(prompt: str, context: str = "", temperature: float = 0.7) -> str:
    """
    Simplified chat interface for quick interactions.
    
    Args:
        prompt: User prompt
        context: Optional context to include
        temperature: Sampling temperature
    
    Returns:
        Generated text response
    
    Example:
        response = await simple_chat("Explain quantum computing")
    """
    client = get_openai_client()
    
    messages = []
    if context:
        messages.append({"role": "system", "content": context})
    messages.append({"role": "user", "content": prompt})
    
    response = await client.chat_completion(
        messages=messages,
        temperature=temperature,
    )
    
    return client.extract_content(response)
