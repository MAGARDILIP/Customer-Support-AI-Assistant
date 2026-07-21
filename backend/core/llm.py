"""
GROQ LLM client wrapper.
Provides a unified interface to interact with the GROQ API.
"""
import logging
from groq import Groq
from backend.config import settings
from backend.core.exceptions import LLMException

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper around the GROQ SDK for chat completions."""

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise LLMException("GROQ_API_KEY is not set in environment variables.")
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        logger.info(f"LLM Client initialized with model: {self.model}")

    FALLBACK_MODEL = "llama-3.3-70b-versatile"

    def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        system_prompt: str | None = None,
    ) -> str:
        """
        Send a chat completion request to GROQ.
        Falls back to llama-3.3-70b-versatile if the primary model fails.

        Args:
            messages: List of message dicts with 'role' and 'content'.
            temperature: Sampling temperature (0.0-1.0).
            max_tokens: Maximum tokens in response.
            system_prompt: Optional system message prepended to conversation.

        Returns:
            The assistant's response text.
        """
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        # Try primary model first
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        except Exception as primary_error:
            logger.warning(f"Primary model '{self.model}' failed: {primary_error}")

            # Fallback to known working model
            if self.model != self.FALLBACK_MODEL:
                logger.info(f"Falling back to model: {self.FALLBACK_MODEL}")
                try:
                    response = self.client.chat.completions.create(
                        model=self.FALLBACK_MODEL,
                        messages=full_messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    logger.info(f"Fallback model succeeded. Switching default to {self.FALLBACK_MODEL}")
                    self.model = self.FALLBACK_MODEL  # Auto-switch for future calls
                    return response.choices[0].message.content
                except Exception as fallback_error:
                    logger.error(f"Fallback model also failed: {fallback_error}")
                    raise LLMException(f"Both models failed. Primary: {primary_error}, Fallback: {fallback_error}")
            else:
                raise LLMException(f"LLM call failed: {str(primary_error)}")

    def quick_response(self, prompt: str, system_prompt: str | None = None) -> str:
        """Simple single-turn response."""
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages, system_prompt=system_prompt)

    def test_connection(self) -> bool:
        """Test if the GROQ API is reachable and the model works."""
        try:
            response = self.quick_response("Say 'OK' if you can hear me.")
            logger.info(f"LLM connection test passed. Response: {response[:50]}")
            return True
        except Exception as e:
            logger.error(f"LLM connection test failed: {e}")
            return False


# Singleton instance
_llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create the singleton LLM client."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
