"""
Author: Shawn
Date: 2023-09-26 13:02:22
LastEditTime: 2023-10-19 21:48:03
"""
import os
from typing import List
import os
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from trendychat.tools.timer import timer_decorator
import threading


class SingletonBlobServiceClient:
    _instance = None
    _client = None
    _lock = threading.Lock()

    def __new__(cls, connection_string=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SingletonBlobServiceClient, cls).__new__(cls)

                # 初始化 BlobServiceClient
                if connection_string:
                    cls._client = BlobServiceClient.from_connection_string(
                        connection_string
                    )
        return cls._instance

    @classmethod
    def get_client(cls):
        if cls._client is None:
            raise ValueError(
                "BlobServiceClient is not initialized. Please ensure connection string is provided during the first instantiation."
            )
        return cls._client


def create_container(container_name: str, connection_string: str) -> None:
    """
    Create a new container in Azure Blob Storage if it doesn't exist.

    Args:
        container_name (str): The name of the container to be created or checked.
        connection_string (str): The connection string for Azure Blob Storage.
    """
    blob_service_client = SingletonBlobServiceClient(connection_string).get_client()

    # Check if the container exists
    try:
        blob_service_client.create_container(container_name)
        print(f"Container '{container_name}' created successfully.")
    except Exception as e:
        # Azure storage will raise an error if the container already exists. We can safely ignore it.
        if "The specified container already exists" not in str(e):
            raise  # If it's another error, re-raise it.

    print(f"Container '{container_name}' already exists or created successfully.")


# @timer_decorator
def refresh_storage_document_url(
    document_name: str,
    container_name: str,
    account_name: str,
    account_key: str,
    duration: int = 24,
):
    # # 設定SAS權限和到期時間
    sas_permission = BlobSasPermissions(read=True)
    expire_time = datetime.utcnow() + timedelta(hours=duration)  # 設置SAS URL在1小時後到期

    # 生成SAS token
    sas_token = generate_blob_sas(
        account_name=account_name,
        account_key=account_key,
        container_name=container_name,
        blob_name=document_name,
        permission=sas_permission,
        expiry=expire_time,
    )

    # 創建SAS URL
    return f"https://{account_name}.blob.core.windows.net/{container_name}/{document_name}?{sas_token}"


# @timer_decorator
def upload_document_to_storage(
    document, document_name: str, container_name: str, connection_string: str
):
    import time

    start_time = time.time()
    blob_service_client = SingletonBlobServiceClient(connection_string).get_client()
    # 上傳檔案

    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=document_name
    )
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"SingletonBlobServiceClient took {elapsed_time:.2f} seconds to run.")

    start_time = time.time()
    blob_client.upload_blob(document, overwrite=True)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"upload_blob took {elapsed_time:.2f} seconds to run.")

    print(f"{document_name} has been uploaded to blob storage.")


# @timer_decorator
def upload_local_document_to_storage(
    document_path: str, container_name: str, connection_string: str
):
    document_name = os.path.basename(document_path)
    # 建立 BlobServiceClient
    with open(document_path, "rb") as document:
        upload_document_to_storage(
            document=document,
            document_name=document_name,
            container_name=container_name,
            connection_string=connection_string,
        )


# @timer_decorator
def get_storage_file(
    container_name: str,
    document_name: str,
    connection_string: str,
    chunk_size=1000,
    chunk_overlap=0,
    separators=[" ", ",", "\n"],
) -> List:
    from langchain.document_loaders import AzureBlobStorageFileLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    loader = AzureBlobStorageFileLoader(
        conn_str=connection_string,
        container=container_name,
        blob_name=document_name,
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=separators
    )

    docs = loader.load_and_split(text_splitter)

    return docs


# @timer_decorator
def delete_storage_file(
    document_name: str, container_name: str, connection_string: str
) -> bool:
    try:
        # 建立 BlobServiceClient
        blob_service_client = SingletonBlobServiceClient(connection_string).get_client()

        # 取得blob的客戶端
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=document_name
        )

        # 刪除blob
        blob_client.delete_blob()

        print(f"'{document_name}' has been deleted from blob storage.")
        return True  # 刪除成功
    except Exception as e:
        print(f"Error deleting '{document_name}': {str(e)}")
        return False  # 刪除失敗或其他錯誤


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    document_path = "/Users/shawnshiu/AccuHit/Consultant/環境準備 - Hands-On Workshop_Atlas Vector Search.pdf"
    container_name = os.environ.get("STORAGE_ACCOUNT_CONTAINER_NAME")

    STORAGE_ACCOUNT_NAME = os.environ.get("STORAGE_ACCOUNT_NAME")
    STORAGE_ACCOUNT_KEY = os.environ.get("STORAGE_ACCOUNT_KEY")
    connection_string = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
    # connection_string = os.environ.get("STORAGE_ACCOUNT_CONNECTION_STRING")
    upload_local_document_to_storage(
        document_path=document_path,
        container_name=container_name,
        connection_string=connection_string,
    )
    # delete_storage_file(
    #     "環境準備 - Hands-On Workshop_Atlas Vector Search.pdf", container_name, connection_string)
    data = get_storage_file(
        container_name=container_name,
        document_name="環境準備 - Hands-On Workshop_Atlas Vector Search.pdf",
        connection_string=connection_string,
    )
    breakpoint()
