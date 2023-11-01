import random
from typing import Dict, List, Optional
from dotenv import load_dotenv
from trendychat.tools.formate_transformer import json2parameters
import os

load_dotenv()


def rename_keys(mapping, key_mapping):
    """Rename keys in a dictionary and filter out the ones not in key_mapping."""
    return {key_mapping[k]: mapping[k] for k in mapping.keys() if k in key_mapping}


class LLMConfig:
    def __init__(
        self,
        config: Optional[List[Dict]] = None,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        top_p: float = 0.95,
        frequency_penalty: float = 0,
        presence_penalty: float = 0,
        stop: Optional[List[str]] = None,
    ) -> None:
        self.model_params = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stop": stop,
        }
        llm_params = os.environ.get("LLM_CANDIDATES")
        llm_params = json2parameters(llm_params)
        if not config:
            num = len(llm_params)
            if num == 0:
                raise ValueError(
                    "No LLM_CANDIDATES found in the environment variables."
                )
            else:
                rename = {
                    "type": "api_type",
                    "version": "api_version",
                    "endpoint": "api_base",
                    "key": "api_key",
                    "name": "engine",
                    "model": "model",
                }
                for model_idx, values in llm_params.items():
                    result = rename_keys(mapping=values, key_mapping=rename)
                    missing_keys = [k for k, v in rename.items() if v not in result]
                    if missing_keys:
                        print(
                            f"Warning: Missing keys {missing_keys} for model_idx: {model_idx}"
                        )
                        continue  # skip this model_idx
                    llm_params[model_idx] = result

        self.config = llm_params

    def get(self) -> Dict:
        random_key = random.choice(list(self.config.keys()))
        selected_config = self.config[random_key]

        print(f"Selected config at LLM name: {random_key}")

        merged_config = {**selected_config, **self.model_params}
        return merged_config


class EbeddingConfig:
    def __init__(self, config: Optional[List[Dict]] = None) -> None:
        self.model_params = {}
        params = os.environ.get("EMBEDDING_CANDIDATES")
        params = json2parameters(params)
        if not config:
            num = len(params)
            if num == 0:
                raise ValueError(
                    "No EMBEDDING_CANDIDATES found in the environment variables."
                )
            else:
                rename = {
                    "type": "openai_api_type",
                    "version": "openai_api_version",
                    "endpoint": "openai_api_base",
                    "key": "openai_api_key",
                    "name": "deployment",
                    "model": "model",
                }
                for model_idx, values in params.items():
                    result = rename_keys(mapping=values, key_mapping=rename)
                    missing_keys = [k for k, v in rename.items() if v not in result]
                    if missing_keys:
                        print(
                            f"Warning: Missing keys {missing_keys} for model_idx: {model_idx}"
                        )
                        continue  # skip this model_idx
                    params[model_idx] = result

        self.config = params

    def get(self) -> Dict:
        random_key = random.choice(list(self.config.keys()))
        selected_config = self.config[random_key]

        print(f"Selected config at Embedding index: {random_key}")

        merged_config = {**selected_config, **self.model_params}
        return merged_config
