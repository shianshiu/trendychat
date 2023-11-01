"""
Author: Shawn
Date: 2023-10-04 14:52:50
LastEditTime: 2023-10-11 17:08:01
"""
from typing import List
from pymongo import MongoClient
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from langchain.vectorstores import MongoDBAtlasVectorSearch

# from tools.db_connector import MongoSingleton


def upload_file_to_vector_store(
    documents: List[Document],
    collection,
    collection_index: str,
    embeddings: OpenAIEmbeddings,
) -> MongoDBAtlasVectorSearch:
    vectorstore = MongoDBAtlasVectorSearch.from_documents(
        documents=documents,
        embedding=embeddings,
        collection=collection,
        index_name=collection_index,
    )
    return vectorstore


def delete_file_in_vector_store(file_name, collection):
    # 根據file_name和source欄位來刪除文件
    result = collection.delete_many({"file_name": file_name, "source": "raw"})
    deleted_count = result.deleted_count
    print(f"{deleted_count} document(s) deleted.")
    # 回傳被刪除的文件數量
    return deleted_count
