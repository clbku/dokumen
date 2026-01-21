"""
LLM Provider Utility Module

This module provides a centralized way to configure and retrieve LLM instances
from different providers (Z.AI, Google Gemini, etc.) for use in Deep-Spec AI agents.

Usage:
    from src.utils.llm_provider import get_llm, LLMProvider

    # Get LLM by provider enum
    llm = get_llm(LLMProvider.ZAI)

    # Or get by string name
    llm = get_llm("zai")
"""

import os
from enum import Enum
from typing import Optional, Literal
from crewai import LLM
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMProvider(str, Enum):
    """
    Supported LLM providers for Deep-Spec AI.
    """
    ZAI = "zai"
    GOOGLE = "google"


class ModelConfig(str, Enum):
    """
    Pre-configured model names for each provider.
    """
    # Z.AI Models (via OpenAI-compatible API)
    ZAI_FLASH = "glm-4.5-air"  # Fast, cost-effective
    ZAI_STANDARD = "glm-4.7"   # Balanced performance
    ZAI_ADVANCED = "glm-4.7"  # Highest quality

    # Google Gemini Models
    GEMINI_FLASH = "gemini/gemini-3-flash-preview"  # Fast, experimental
    GEMINI_PRO = "gemini/gemini-3-pro-preview"   # High quality
    GEMINI_THINKING = "gemini/gemini-3-pro-preview"  # Complex reasoning


# Provider-specific configuration
PROVIDER_CONFIG = {
    LLMProvider.ZAI: {
        "env_key": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_API_BASE",
        "default_model": ModelConfig.ZAI_STANDARD,
        "default_temperature": 0.3,
        "default_timeout": 120,
    },
    LLMProvider.GOOGLE: {
        "env_key": "GOOGLE_API_KEY",
        "base_url_env": None,
        "default_model": ModelConfig.GEMINI_PRO,
        "default_temperature": 0.5,
        "default_timeout": 120,
    },
}


def get_llm(
    provider: LLMProvider | str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    timeout: Optional[int] = None,
    verbose: bool = False,
) -> LLM:
    """
    Factory function to get an LLM instance based on the provider.

    Args:
        provider: The LLM provider (LLMProvider enum or string: "zai", "google")
        model: Specific model name to use. If None, uses provider's default.
        temperature: Sampling temperature (0.0 - 2.0). If None, uses provider's default.
        timeout: Request timeout in seconds. If None, uses provider's default.
        verbose: Whether to enable verbose logging.

    Returns:
        LLM: Configured CrewAI LLM instance

    Raises:
        ValueError: If provider is unknown or required environment variables are missing

    Examples:
        >>> # Get default Z.AI LLM
        >>> llm = get_llm(LLMProvider.ZAI)

        >>> # Get specific Gemini model with custom temperature
        >>> llm = get_llm("google", model="gemini/gemini-2.0-flash-exp", temperature=0.7)
    """
    # Normalize provider to enum
    if isinstance(provider, str):
        provider = provider.lower()
        try:
            provider = LLMProvider(provider)
        except ValueError:
            raise ValueError(
                f"Unknown provider: '{provider}'. "
                f"Supported providers: {[p.value for p in LLMProvider]}"
            )

    # Get provider config
    config = PROVIDER_CONFIG.get(provider)
    if not config:
        raise ValueError(f"No configuration found for provider: {provider}")

    # Get API key
    api_key = os.getenv(config["env_key"])
    if not api_key:
        raise ValueError(
            f"API key not found for provider '{provider.value}'. "
            f"Please set environment variable: {config['env_key']}"
        )

    # Set defaults
    model = model or config["default_model"].value
    temperature = temperature if temperature is not None else config["default_temperature"]
    timeout = timeout if timeout is not None else config["default_timeout"]

    # Build LLM kwargs
    llm_kwargs = {
        "model": model,
        "api_key": api_key,
        "temperature": temperature,
        "timeout": timeout,
    }

    # Add base_url for Z.AI (OpenAI-compatible)
    if provider == LLMProvider.ZAI:
        base_url = os.getenv(config["base_url_env"])
        if not base_url:
            print(f"Warning: {config['base_url_env']} not found. Using default OpenAI endpoint.")
        else:
            llm_kwargs["base_url"] = base_url

    # Create and return LLM instance
    try:
        return LLM(**llm_kwargs)
    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize LLM for provider '{provider.value}': {e}"
        )


def get_zai_llm(
    model: Optional[str] = None,
    temperature: float = 0.3,
    timeout: int = 120,
) -> LLM:
    """
    Convenience function to get a Z.AI LLM instance.

    Z.AI is best suited for:
    - Structured output generation (JSON, schemas)
    - Fast reasoning and logic tasks
    - Chinese language processing
    """
    return get_llm(
        provider=LLMProvider.ZAI,
        model=model or ModelConfig.ZAI_STANDARD.value,
        temperature=temperature,
        timeout=timeout,
    )


def get_google_llm(
    model: Optional[str] = None,
    temperature: float = 0.5,
    timeout: int = 120,
) -> LLM:
    """
    Convenience function to get a Google Gemini LLM instance.

    Google Gemini is best suited for:
    - Complex reasoning and analysis
    - Multi-step problem solving
    - Creative and innovative thinking
    - Long context understanding
    """
    return get_llm(
        provider=LLMProvider.GOOGLE,
        model=model or ModelConfig.GEMINI_PRO.value,
        temperature=temperature,
        timeout=timeout,
    )


# Provider recommendations for different agent roles
AGENT_PROVIDER_RECOMMENDATIONS = {
    "white_hat": {
        "provider": LLMProvider.ZAI,
        "model": ModelConfig.ZAI_STANDARD,
        "reason": "Structured output for architecture design, precise technical details",
        "temperature": 0.2,  # Low temperature for consistency
    },
    "black_hat": {
        "provider": LLMProvider.GOOGLE,
        "model": ModelConfig.GEMINI_THINKING,
        "reason": "Complex reasoning for finding edge cases and vulnerabilities",
        "temperature": 0.7,  # Higher temperature for creative problem-finding
    },
    "green_hat": {
        "provider": LLMProvider.GOOGLE,
        "model": ModelConfig.GEMINI_PRO,
        "reason": "Balanced decision-making with good reasoning capabilities",
        "temperature": 0.4,  # Moderate temperature for balanced judgment
    },
}


def get_agent_llm(agent_role: Literal["white_hat", "black_hat", "green_hat"]) -> LLM:
    """
    Get the recommended LLM for a specific agent role.

    This function uses pre-configured provider and model recommendations
    optimized for each agent's purpose.

    Args:
        agent_role: The role of the agent ("white_hat", "black_hat", or "green_hat")

    Returns:
        LLM: Optimized LLM instance for the agent role

    Examples:
        >>> # Get LLM for BlackHat agent
        >>> black_hat_llm = get_agent_llm("black_hat")
    """
    config = AGENT_PROVIDER_RECOMMENDATIONS.get(agent_role)
    if not config:
        raise ValueError(f"Unknown agent role: {agent_role}")

    return get_llm(
        provider=config["provider"],
        model=config["model"].value,
        temperature=config["temperature"],
    )
