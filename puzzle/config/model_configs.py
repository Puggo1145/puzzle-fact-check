# Load environment variables from .env (located in the project root directory)
import os
from dotenv import load_dotenv

# Determine the path to the .env file (assuming it's one level up from the current config directory)
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)


def str_to_list(value):
    """Converts a comma separated string into a list of strings."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

# Provider configurations. Models are categorized as reasoning, non-reasoning, and light models.
PROVIDERS_CONFIG = {
    "openai": {
        # "api_key": os.getenv("OPENAI_API_KEY"),
        "reasoning_models": str_to_list(os.getenv("OPENAI_REASONING_MODELS")),
        "non_reasoning_models": str_to_list(os.getenv("OPENAI_NON_REASONING_MODELS")),
        "light_models": str_to_list(os.getenv("OPENAI_LIGHT_MODELS"))
    },
    "qwen": {
        # "api_key": os.getenv("QWEN_API_KEY"),
        "reasoning_models": str_to_list(os.getenv("QWEN_REASONING_MODELS")),
        "non_reasoning_models": str_to_list(os.getenv("QWEN_NON_REASONING_MODELS")),
        "light_models": str_to_list(os.getenv("QWEN_LIGHT_MODELS"))
    },
    "deepseek": {
        # "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "reasoning_models": str_to_list(os.getenv("DEEPSEEK_REASONING_MODELS")),
        "non_reasoning_models": str_to_list(os.getenv("DEEPSEEK_NON_REASONING_MODELS")),
        "light_models": str_to_list(os.getenv("DEEPSEEK_LIGHT_MODELS"))
    }
    # Additional providers (e.g., gemini) can be added similarly
}

# Agent restrictions configuration. These specify models that are excluded for different agent types.
AGENT_RESTRICTIONS = {
    "main_agent": {
        "excluded": str_to_list(os.getenv("MAIN_AGENT_EXCLUDED_MODELS"))
    },
    "metadata_extractor": {
        "excluded": str_to_list(os.getenv("METADATA_EXTRACTOR_EXCLUDED_MODELS"))
    },
    "searcher": {
        "excluded": str_to_list(os.getenv("SEARCHER_EXCLUDED_MODELS"))
    }
}

# Consolidated model configurations
MODEL_CONFIGS = {
    "providers": PROVIDERS_CONFIG,
    "agent_restrictions": AGENT_RESTRICTIONS
}

if __name__ == "__main__":
    # For testing purposes: print the model configurations in JSON format
    import json
    print(json.dumps(MODEL_CONFIGS, indent=4))

