import time
import os
import asyncio
from functools import partial
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

from langchain.vectorstores import MongoDBAtlasVectorSearch
from trendychat.tools.db_connector import MongoSingleton
from trendychat.prompt_manager.chat_prompt_v2 import ChatPrompt
from trendychat.configs import EbeddingConfig, LLMConfig
from trendychat.llm import openai_reponse, async_openai_reponse, get_embedding_model

from pydantic import BaseModel
from datetime import datetime


class MemoryMessage(BaseModel):
    """
    'reference' coontain 'vector_id', 'document_id', 'document_name', 'document_source', 'created_at'
    """

    user_text: Optional[str] = None
    bot_text: Optional[str] = None
    user_timestamp: Optional[datetime] = None
    bot_timestamp: Optional[datetime] = None
    reference: List[dict] = []
    history: List[str] = []
    context: List[str] = []


embedding_config = EbeddingConfig()
gpt_config = LLMConfig()
REFERENCE_NUMBER = int(os.getenv("REFERENCE_NUMBER", "3"))


def get_relavent_contexts(text: str, num_references: int = REFERENCE_NUMBER):
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
        documents = vectorstore.similarity_search(query=text, k=num_references)
        reference = []
        context = []

        for i in range(len(documents)):
            context.append(documents[i].page_content)
            reference.append(
                {
                    "vector_id": documents[i].metadata.get("_id", None),
                    "document_id": documents[i].metadata.get("document_id", None),
                    "document_name": documents[i].metadata.get("document_name", None),
                    "document_source": documents[i].metadata.get(
                        "document_source", None
                    ),
                    "created_at": documents[i].metadata.get("created_at", None),
                }
            )

    except Exception as e:
        reference = []
        context = []
        raise RuntimeError(
            f"An error occurred during 'get_relavent_contexts': {str(e)}"
        )

    pack = {
        "context": context,
        "reference": reference,
    }
    return pack


async def get_relavent_contexts_async(
    text: str, num_references: int = REFERENCE_NUMBER
):
    loop = asyncio.get_running_loop()
    # 使用 functools.partial 包装同步函数及其参数
    func = partial(get_relavent_contexts, text, num_references)
    # 在执行器中运行同步函数
    pack = await loop.run_in_executor(None, func)
    return pack


def reply_message(user_text: str, history: List[str], context: List[str]):
    try:
        messages = ChatPrompt.get_message(
            user_text=user_text, history=history, context=context
        )
        model_config = gpt_config.get()
        messages = openai_reponse(messages=messages, model_config=model_config)
    except Exception as e:
        raise RuntimeError(f"An error occurred during 'reply_message': {str(e)}")

    return messages


async def reply_message_async(user_text: str, history: List[str], context: List[str]):
    try:
        messages = ChatPrompt.get_message(
            user_text=user_text, history=history, context=context
        )
        # print("\nmessages\n:", messages, "\n")
        model_config = gpt_config.get()
        messages = await async_openai_reponse(
            messages=messages, model_config=model_config
        )
        # 从响应中提取出消息内容
        return messages
    except Exception as e:
        raise RuntimeError(f"An error occurred during 'reply_message_async': {str(e)}")


class MemoryChat:
    @classmethod
    def reply(cls, chat_message: MemoryMessage) -> MemoryMessage:
        text = str(chat_message.user_text)
        pack = get_relavent_contexts(text=text, num_references=3)
        context = pack.get("context", [])
        reference = pack.get("reference", [])

        if REFERENCE_NUMBER > 3:
            EXTRA_NUMBER = REFERENCE_NUMBER - 3
            text = str(chat_message.history + [chat_message.user_text])
            subpack = get_relavent_contexts(
                text=text, num_references=EXTRA_NUMBER
            )  # 這邊要修正成只選EXTRA_NUMBER個
            context += subpack.get("context", [])
            reference += subpack.get("reference", [])
        chat_message.context = context
        chat_message.reference = reference

        response = reply_message(
            user_text=chat_message.user_text,
            history=chat_message.history,
            context=chat_message.context,
        )
        chat_message.bot_timestamp = datetime.now()
        chat_message.bot_text = response["choices"][0]["message"]["content"]
        return chat_message

    @classmethod
    async def async_reply(cls, chat_message: MemoryMessage) -> MemoryMessage:
        text = chat_message.user_text
        EXTRA_NUMBER = max(REFERENCE_NUMBER - 3, 0)

        # start_time = time.perf_counter()  # TODO: 開始計時
        # 根据 EXTRA_NUMBER 是否大于0来决定是否进行第二次查询
        if EXTRA_NUMBER > 0:
            # 用于构建第二次调用的文本
            combined_text = " ".join(chat_message.history + [text])

            # 同时进行两次查询
            pack, subpack = await asyncio.gather(
                get_relavent_contexts_async(text=text, num_references=3),
                get_relavent_contexts_async(
                    text=combined_text, num_references=EXTRA_NUMBER
                ),
            )
        else:
            # 只进行一次查询
            pack = await get_relavent_contexts_async(text=text, num_references=3)
            subpack = {"context": [], "reference": []}

        # context_time = time.perf_counter()  # TODO: 计时结束
        # print(f"Context generation time: {context_time - start_time:.2f} seconds")

        # 合并结果
        context = pack.get("context", []) + subpack.get("context", [])
        reference = pack.get("reference", []) + subpack.get("reference", [])

        chat_message.context = context
        chat_message.reference = reference

        # start_time = time.perf_counter()  # TODO: 開始計時
        response = await reply_message_async(
            user_text=text, history=chat_message.history, context=context
        )
        # reply_time = time.perf_counter()  # TODO: 计时结束
        # print(
        #     f"Reply generation time: {reply_time - start_time:.2f} seconds"
        # )  # TODO: 计时结束

        chat_message.bot_timestamp = datetime.now()
        chat_message.bot_text = response["choices"][0]["message"]["content"]
        return chat_message
