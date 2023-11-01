"""
Author: Shawn
Date: 2023-09-25 14:36:17
LastEditTime: 2023-09-25 20:39:08
"""


from trendychat.tools.timer import timer_decorator
from langchain.embeddings import OpenAIEmbeddings
import openai
from typing import Dict, List


def openai_reponse(messages: List[Dict], model_config: Dict):
    try:
        response = openai.ChatCompletion.create(messages=messages, **model_config)
    except Exception as e:
        raise RuntimeError(f"An error occurred during OpenAI response: {str(e)}")
    return response


def get_embedding_model(model_config: Dict):
    return OpenAIEmbeddings(**model_config)


def embedding_reponse(message: str, model_config: Dict) -> List[float]:
    """
    Args:
        text (str): _description_
        model_config (Dict): {
            "deployment":"TEST2",
            "model":"text-embedding-ada-002",
            "openai_api_type":"azure",
            "openai_api_key":"696cc4687b03490e9a55d9961f1c3131",
            "openai_api_base":"https://test20230831246.openai.azure.com/",
            "openai_api_version":"2023-05-15"
        }

    """
    try:
        embeddings = OpenAIEmbeddings(**model_config)
        response = embeddings.embed_query(message)
    except Exception as e:
        raise RuntimeError(f"An error occurred during Embedding response: {str(e)}")
    return response
