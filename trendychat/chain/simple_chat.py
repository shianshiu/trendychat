"""
Author: Shawn
Date: 2023-09-27 16:52:23
LastEditTime: 2023-10-04 14:43:06
"""
"""
TODO: Implement a simple chat that just returns the message

- tranform quesiton into vector by embedding process
- search similarity between question and context
- combine the context, question and system prompt
- generate answer by chat model
"""
import asyncio
from langchain.vectorstores import MongoDBAtlasVectorSearch
from trendychat.tools.db_connector import MongoSingleton
from trendychat.prompt_manager.chat_prompt import ChatPrompt
from trendychat.configs import EbeddingConfig, LLMConfig
from trendychat.llm import openai_reponse, get_embedding_model
import os
from dotenv import load_dotenv

load_dotenv()

embedding_config = EbeddingConfig()
gpt_config = LLMConfig()


def get_relavent_contexts(message: str):
    try:
        db_name = os.getenv("MONGODB_DATABASE_NANE")
        collection_name = os.getenv("MONGODB_COLLECTION_VECTOR")
        mongo_instance = MongoSingleton()
        collection = mongo_instance[db_name][collection_name]
        index_name = os.getenv("MONGODB_COLLECTION_VECTOR_SPECIAL_INDEX")

        model_config = embedding_config.get()
        embeddings = get_embedding_model(model_config=model_config)

        vectorstore = MongoDBAtlasVectorSearch(
            collection=collection, embedding=embeddings, index_name=index_name
        )
        contexts = vectorstore.similarity_search(query=message, k=3)
        contexts = [contexts[i].page_content for i in range(len(contexts))]

    except Exception as e:
        raise RuntimeError(
            f"An error occurred during 'get_relavent_contexts': {str(e)}"
        )
    return contexts


def reply_message(message: str, contexts: list):
    try:
        messages = ChatPrompt.get_message(message=message, context=contexts)
        model_config = gpt_config.get()
        message = openai_reponse(messages=messages, model_config=model_config)
    except Exception as e:
        raise RuntimeError(f"An error occurred during 'reply_message': {str(e)}")

    return message


class SimpleChat:
    @classmethod
    def reply(cls, message):
        contexts = get_relavent_contexts(message=message)  # 確保這也是異步的
        for cnt in contexts:
            print(cnt)
        response = reply_message(message=message, contexts=contexts)
        return response["choices"][0]["message"]["content"]  # TODO:
        # return response

    # async def reply_async(self, message):
    #     contexts = get_relavent_contexts(message=message)  # 確保這也是異步的
    #     response = reply_message(message=message, contexts=contexts)
    #     return response['choices'][0]['message']['content']

    # @classmethod
    # def reply(cls, message):
    #     instance = cls()  # 創建一個SimpleChat實例
    #     return asyncio.run(instance.reply_async(message))
