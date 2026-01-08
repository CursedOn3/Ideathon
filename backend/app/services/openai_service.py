"""
OpenAI Service Layer

Responsibilities:
• High-level interface for content generation
• Manage conversation context and history
• Format prompts with system instructions
• Handle structured output extraction
• Token management and cost tracking

Architecture Decision:
- Abstracts OpenAI integration complexity from agents
- Provides reusable prompt templates
- Enforces consistent system instructions across agents
- Enables easy switching between models/providers
"""

from typing import List, Dict, Any, Optional
import json

from app.integrations.azure_openai import get_openai_client, AzureOpenAIClient
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class OpenAIService:
    """
    Service layer for Azure OpenAI operations.
    
    Provides high-level methods for content generation with
    consistent prompting, error handling, and logging.
    """
    
    def __init__(self, client: Optional[AzureOpenAIClient] = None):
        """Initialize service with OpenAI client."""
        self.client = client or get_openai_client()
    
    async def generate_with_context(
        self,
        prompt: str,
        context: str = "",
        system_instruction: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """
        Generate content with optional context and system instructions.
        
        Args:
            prompt: User prompt
            context: Additional context (e.g., retrieved documents)
            system_instruction: System-level instructions
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text content
        """
        messages = []
        
        # Add system instruction
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        # Add context if provided
        if context:
            context_message = f"Context:\n{context}\n\nBased on the above context, please respond to the following:"
            messages.append({"role": "system", "content": context_message})
        
        # Add user prompt
        messages.append({"role": "user", "content": prompt})
        
        logger.debug(f"Generating content with {len(messages)} messages")
        
        response = await self.client.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        content = self.client.extract_content(response)
        tokens = self.client.get_token_count(response)
        
        logger.info(
            f"Generated content",
            extra={
                "tokens_used": tokens["total_tokens"],
                "content_length": len(content),
            }
        )
        
        return content
    
    async def generate_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output.
        
        Args:
            prompt: User prompt
            output_schema: Expected JSON schema
            context: Optional context
        
        Returns:
            Parsed JSON object
        """
        system_instruction = f"""You are a helpful assistant that generates structured JSON output.
Always respond with valid JSON matching this schema:
{json.dumps(output_schema, indent=2)}

Do not include any text outside the JSON object."""
        
        content = await self.generate_with_context(
            prompt=prompt,
            context=context,
            system_instruction=system_instruction,
            temperature=0.3,  # Lower temperature for structured output
        )
        
        # Extract JSON from response
        try:
            # Try to parse as JSON
            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
                return json.loads(json_str)
            else:
                logger.error(f"Failed to parse JSON from response: {content[:200]}")
                raise ValueError("Response is not valid JSON")


# Global service instance
_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    """Get or create global OpenAI service instance."""
    global _service
    if _service is None:
        _service = OpenAIService()
    return _service
