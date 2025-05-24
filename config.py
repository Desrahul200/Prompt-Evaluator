from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
DEFAULT_TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
DEFAULT_TIMEOUT = int(os.getenv("TIMEOUT", "600"))

def get_llm_config() -> Dict[str, Any]:
    if os.getenv("GROQ_API_KEY"):
        return {
            "temperature": DEFAULT_TEMPERATURE,
            "timeout": DEFAULT_TIMEOUT,
            "config_list": [
                {
                    "model": "llama3-70b-8192",
                    "api_key": os.getenv("GROQ_API_KEY"),
                    "base_url": "https://api.groq.com/openai/v1",
                    "price": [0.0, 0.0],
                }
            ],
        }

    if os.getenv("OPENAI_API_KEY"):
        return {
            "temperature": DEFAULT_TEMPERATURE,
            "timeout": DEFAULT_TIMEOUT,
            "config_list": [
                {
                    "model": "gpt-4",
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "base_url": "https://api.openai.com/v1",
                    "price": [0.03, 0.06],
                }
            ],
        }

    if os.getenv("ANTHROPIC_API_KEY"):
        return {
            "temperature": DEFAULT_TEMPERATURE,
            "timeout": DEFAULT_TIMEOUT,
            "config_list": [
                {
                    "model": "claude-3-opus-20240229",
                    "api_key": os.getenv("ANTHROPIC_API_KEY"),
                    "base_url": "https://api.anthropic.com/v1",
                    "price": [0.015, 0.015],
                }
            ],
        }

    # fallback to local Ollama
    return {
        "temperature": DEFAULT_TEMPERATURE,
        "timeout": DEFAULT_TIMEOUT,
        "config_list": [
            {
                "model": "llama2",
                "api_key": "ollama",
                "base_url": DEFAULT_BASE_URL,
                "price": [0.0, 0.0],
            }
        ],
    }

def update_config_for_model(selected: str) -> Dict[str, Any]:
    if selected.startswith("GPT-4") and os.getenv("OPENAI_API_KEY"):
        return {
            "temperature": DEFAULT_TEMPERATURE,
            "timeout": DEFAULT_TIMEOUT,
            "config_list": [
                {
                    "model": "gpt-4",
                    "api_key": os.getenv("OPENAI_API_KEY"),
                    "base_url": "https://api.openai.com/v1",
                    "price": [0.03, 0.06],
                }
            ],
        }
    if selected.startswith("Claude") and os.getenv("ANTHROPIC_API_KEY"):
        return {
            "temperature": DEFAULT_TEMPERATURE,
            "timeout": DEFAULT_TIMEOUT,
            "config_list": [
                {
                    "model": "claude-3-opus-20240229",
                    "api_key": os.getenv("ANTHROPIC_API_KEY"),
                    "base_url": "https://api.anthropic.com/v1",
                    "price": [0.015, 0.015],
                }
            ],
        }
    if selected == "Other Ollama Model":
        return {
            "temperature": DEFAULT_TEMPERATURE,
            "timeout": DEFAULT_TIMEOUT,
            "config_list": [
                {
                    "model": "llama2",
                    "api_key": "ollama",
                    "base_url": DEFAULT_BASE_URL,
                    "price": [0.0, 0.0],
                }
            ],
        }
    return get_llm_config()

SUPPORTED_MODELS = [
    "Mixtral (Groq/Ollama - Default)",
    "GPT-4 (OpenAI)",
    "Claude (Anthropic)",
    "Other Ollama Model",
]
