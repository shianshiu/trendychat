"""
Author: Shawn
Date: 2023-09-25 14:59:13
LastEditTime: 2023-10-20 17:49:33
"""

from pymongo.errors import PyMongoError
import time
from datetime import datetime, timedelta
import asyncio
from trendychat.tools.db_connector import MongoSingleton
from typing import List, Tuple, Dict
from trendychat.tools.timer import get_current_time
from trendychat.tools.token_counter import count_token_number
from trendychat.document_storage import (
    upload_local_document_to_storage,
    upload_document_to_storage,
    refresh_storage_document_url,
    get_storage_file,
    delete_storage_file,
    create_container
)
from trendychat.vector_store import upload_file_to_vector_store
from trendychat.configs import EbeddingConfig
from trendychat.llm import get_embedding_model
from bson.objectid import ObjectId
import os
import re
import logging
from tqdm import tqdm
from pymongo.errors import CollectionInvalid, DuplicateKeyError, OperationFailure

async def run_upload_tasks(tasks):
    await asyncio.gather(*tasks)


def create_collection_role(db_name: str, collection_name: str):
    # from pymongo.errors import CollectionInvalid, DuplicateKeyError, OperationFailure

    client = MongoSingleton()
    db = client[db_name]
    TIMEZONE = os.getenv("TIMEZONE")

    # 嘗試創建集合
    try:
        db.create_collection(collection_name)
    except CollectionInvalid:
        print(f"Collection {collection_name} already exists in {db_name}.")

    collection = db[collection_name]

    # 建立唯一索引於 document_name
    try:
        collection.create_index("name", unique=True)
    except OperationFailure as e:
        print(f"Failed to create unique index on name: {str(e)}")

    # 為其他欄位建立索引
    indexes = ["permissions", "created_at"]

    for index in indexes:
        try:
            collection.create_index(index)
        except OperationFailure as e:
            print(f"Failed to create index on {index}: {str(e)}")

    roles = [
        {
            "name": "後台管理者",
            "permissions": ["manage_users"],
            "created_at": get_current_time(TIMEZONE),
        },
        {"name": "使用者", "permissions": [], "created_at": get_current_time(TIMEZONE)},
    ]

    # 將角色插入集合
    for role in roles:
        role_name = role.get("name")

        # 查詢是否已存在具有相同名稱的角色
        existing_role = collection.find_one({"name": role_name})

        if not existing_role:
            # 如果角色不存在，則嘗試添加到集合中
            try:
                collection.insert_one(role)
            except DuplicateKeyError:
                print(f"A role with the name {role_name} already exists.")
            except Exception as e:
                print(f"An error occurred while inserting role {role_name}: {str(e)}")


def create_collection_document_manager(db_name: str, collection_name: str):
    # from pymongo.errors import CollectionInvalid, OperationFailure

    client = MongoSingleton()
    db = client[db_name]

    # 嘗試創建集合
    try:
        db.create_collection(collection_name)
    except CollectionInvalid:
        print(f"Collection {collection_name} already exists in {db_name}.")

    collection = db[collection_name]

    # 建立唯一索引於 document_name
    try:
        collection.create_index("document_name", unique=True)
    except OperationFailure as e:
        print(f"Failed to create unique index on document_name: {str(e)}")

    # 為其他欄位建立索引
    indexes = ["url", "source", "created_at", "updated_at", "status", "user_name"]

    for index in indexes:
        try:
            collection.create_index(index)
        except OperationFailure as e:
            print(f"Failed to create index on {index}: {str(e)}")


def create_collection_vector_store(db_name: str, collection_name: str):
    # from pymongo.errors import CollectionInvalid, OperationFailure

    client = MongoSingleton()
    db = client[db_name]

    # 嘗試創建集合
    try:
        db.create_collection(collection_name)
    except CollectionInvalid:
        print(f"Collection {collection_name} already exists in {db_name}.")

    collection = db[collection_name]

    # 為欄位建立索引
    indexes = ["document_id", "document_source", "document_name", "created_at"]

    for index in indexes:
        try:
            collection.create_index(index)
        except OperationFailure as e:
            print(f"Failed to create index on {index}: {str(e)}")


def create_collection_example(db_name: str, collection_name: str):
    STORAGE_ACCOUNT_NAME = os.environ.get("STORAGE_ACCOUNT_NAME")
    STORAGE_ACCOUNT_KEY = os.environ.get("STORAGE_ACCOUNT_KEY")
    connection_string = f'DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCOUNT_NAME};AccountKey={STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net'
    container_name = os.environ.get("STORAGE_ACCOUNT_CONTAINER_DEMO_NAME")

    create_container(container_name=container_name,
                    connection_string=connection_string)

    # Check if the data folder exists
    data_path = "./data"
    if not os.path.exists(data_path):
        print("The data folder does not exist or there are no files to upload.")
        return

    MONGODB_URI = os.environ.get("MONGODB_URI")
    MONGODB_DATABASE_NAME = db_name  # Fixed typo here
    MONGODB_COLLECTION_EXAMPLE = collection_name  # Fixed typo here

    client = MongoSingleton(MONGODB_URI)
    db = client[MONGODB_DATABASE_NAME]
    collection = db[MONGODB_COLLECTION_EXAMPLE]

    # Assuming there might be multiple files to upload, we'll loop through the directory
    # Assuming there might be multiple files to upload, we'll loop through the directory
    for file in os.listdir(data_path):
        document_path = os.path.join(data_path, file)
        upload_local_document_to_storage(
            document_path=document_path,
            container_name=container_name,
            connection_string=connection_string
        )

        document_name = os.path.basename(document_path)
        file_url = refresh_storage_document_url(
            document_name=document_name,
            container_name=container_name,
            account_name=STORAGE_ACCOUNT_NAME,
            account_key=STORAGE_ACCOUNT_KEY,
            duration=24
        )

        # Create the collection if it doesn't exist
        try:
            db.create_collection(MONGODB_COLLECTION_EXAMPLE)
        except CollectionInvalid:
            print(f"Collection {MONGODB_COLLECTION_EXAMPLE} already exists in {MONGODB_DATABASE_NAME}.")

        TIMEZONE = os.environ.get("TIMEZONE")
        # The criteria based on which we'll decide to update or insert
        criteria = {"name": "demo_uploading"}

        # The new values that we want to set
        new_values = {"$set": {"url": file_url,
                               "document_name": document_name,
                               "created_at": get_current_time(TIMEZONE),
                               "updated_at": get_current_time(TIMEZONE)}}

        # Using upsert to insert or update the document
        collection.update_one(criteria, new_values, upsert=True)`
    

def create_collection_users(db_name: str, collection_name: str):
    # TODO: name\email\password\role_id
    client = MongoSingleton()
    db = client[db_name]

    # 嘗試創建集合
    try:
        db.create_collection(collection_name)
    except CollectionInvalid:
        print(f"Collection {collection_name} already exists in {db_name}.")

    collection = db[collection_name]

    # 為欄位建立索引
    indexes = ["name", "email", "password", "role_id"]

    for index in indexes:
        try:
            collection.create_index(index)
        except OperationFailure as e:
            print(f"Failed to create index on {index}: {str(e)}")




class ManageDocuments:
    def __init__(self):
        _STORAGE_ACCOUNT_NAME = os.environ.get("STORAGE_ACCOUNT_NAME")
        _STORAGE_ACCOUNT_KEY = os.environ.get("STORAGE_ACCOUNT_KEY")
        self.duration = int(os.getenv("STORAGE_FILE_SAS_TOKEN_DURATION"))
        self.timezone = os.getenv("TIMEZONE")
        self.storage_account_name = _STORAGE_ACCOUNT_NAME
        self.storage_account_key = _STORAGE_ACCOUNT_KEY
        self.storage_connection_string = f"DefaultEndpointsProtocol=https;AccountName={_STORAGE_ACCOUNT_NAME};AccountKey={_STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
        self.storage_container_name = os.getenv("STORAGE_ACCOUNT_CONTAINER_NAME")
        self.storage_container_demo_name = os.getenv(
            "STORAGE_ACCOUNT_CONTAINER_DEMO_NAME"
        )

        self.mongodb_url = os.getenv("MONGODB_URI")
        self.mongodb_database = os.getenv("MONGODB_DATABASE_NANE")
        self.mongodb_collection_example = os.getenv("MONGODB_COLLECTION_EXAMPLE")
        self.mongodb_collection_roles = os.getenv("MONGODB_COLLECTION_ROLE")
        self.mongodb_collection_document_manager = os.getenv(
            "MONGODB_COLLECTION_DOCUMENT_MANAGER"
        )
        self.mongodb_collection_vector = os.getenv("MONGODB_COLLECTION_VECTOR")
        self.mongodb_collection_vector_special_index = os.getenv(
            "MONGODB_COLLECTION_VECTOR_SPECIAL_INDEX"
        )
        self.document_chunk_size = int(os.getenv("DOCUMENT_CHUNK_SIZE"))
        self.document_chunk_overlap = int(os.getenv("DOCUMENT_CHUNK_OVERLAP"))

    def init_database(self):
        create_collection_role(
            db_name=self.mongodb_database, collection_name=self.mongodb_collection_roles
        )
        create_collection_document_manager(
            db_name=self.mongodb_database,
            collection_name=self.mongodb_collection_document_manager,
        )
        create_collection_vector_store(
            db_name=self.mongodb_database,
            collection_name=self.mongodb_collection_vector,
        )

    async def async_upload_document(
        self, doc_name, doc_id, collection, doc_path=None, doc_content=None
    ):
        try:
            if doc_path:
                upload_local_document_to_storage(
                    document_path=doc_path,
                    container_name=self.storage_container_name,
                    connection_string=self.storage_connection_string,
                )
            elif doc_content:
                upload_document_to_storage(
                    document=doc_content,
                    document_name=doc_name,
                    container_name=self.storage_container_name,
                    connection_string=self.storage_connection_string,
                )
            else:
                raise ValueError("Either 'path' or 'doc_content' must be provided.")

            # Get the refreshed URL after uploading the document
            url = refresh_storage_document_url(
                document_name=doc_name,
                container_name=self.storage_container_name,
                account_name=self.storage_account_name,
                account_key=self.storage_account_key,
                duration=self.duration,
            )

            # Update the MongoDB record with the new status, updated_at and the URL
            collection.update_one(
                {"_id": ObjectId(doc_id)},
                {
                    "$set": {
                        "status": "pending",
                        "updated_at": get_current_time(zone=self.timezone),
                        "url": url,
                    }
                },
            )
            print(f"Document: {doc_name} uploaded from {doc_path} to storage.")
        except Exception as e:
            # Here you may want to log the error or perform other error handling
            raise e

    def upload_local_documents_to_storage(
        self, document_paths: List[str], user_name: str = None, source: str = None
    ):
        documents = []
        duplicate_documents = []
        client = MongoSingleton(self.mongodb_url)
        collection = client[self.mongodb_database][
            self.mongodb_collection_document_manager
        ]
        for doc_path in tqdm(document_paths, desc="Uploading documents", unit="file"):
            doc_name = os.path.basename(doc_path)
            print(f"doc_name:{doc_name}")
            if collection.find_one({"document_name": doc_name}):
                print(f"-->Document: {doc_name} already exists in storage.")
                duplicate_documents.append(doc_name)

            else:
                content = {
                    "document_name": doc_name,
                    "created_at": get_current_time(zone=self.timezone),
                    "updated_at": get_current_time(zone=self.timezone),
                    "status": "uploading",
                    "user_name": user_name,
                    "source": source,
                }
                result = collection.insert_one(content)
                doc_id = result.inserted_id
                documents.append(
                    {"doc_path": doc_path, "doc_name": doc_name, "doc_id": doc_id}
                )

        tasks = [
            self.async_upload_document(**param, collection=collection)
            for param in documents
        ]
        # Create a new task to upload documents asynchronously
        if tasks:
            # asyncio.create_task(asyncio.gather(*tasks))
            asyncio.run(run_upload_tasks(tasks))

        if duplicate_documents:
            print("Some document names are duplicated.")
            return duplicate_documents
        else:
            print("Upload process has started for all documents.")
            return None

    def upload_documents_to_storage(
        self, documents: List[Tuple], user_name: str = None, source: str = None
    ):
        """Upload documents to Azure Storage.

        Args:
            documents (List[Tuple]): A list of tuples, each tuple contains a document name and its content.
        """

        fincal_documents = []
        duplicate_documents = []
        client = MongoSingleton(self.mongodb_url)
        collection = client[self.mongodb_database][
            self.mongodb_collection_document_manager
        ]

        for doc_name, doc_content in documents:
            # print(f"doc_name:{doc_name}")
            if collection.find_one({"document_name": doc_name}):
                # print(f"-->Document: {doc_name} already exists in storage.")
                duplicate_documents.append(doc_name)
            else:
                content = {
                    "document_name": doc_name,
                    "created_at": get_current_time(zone=self.timezone),
                    "updated_at": get_current_time(zone=self.timezone),
                    "status": "uploading",
                    "user_name": user_name,
                    "source": source,
                }
                result = collection.insert_one(content)
                doc_id = result.inserted_id
                fincal_documents.append(
                    {"doc_content": doc_content, "doc_name": doc_name, "doc_id": doc_id}
                )

        tasks = [
            self.async_upload_document(**param, collection=collection)
            for param in fincal_documents
        ]
        # Create a new task to upload documents asynchronously
        if tasks:
            asyncio.run(run_upload_tasks(tasks))

        if duplicate_documents:
            print("Some document names are duplicated.")
            return duplicate_documents
        else:
            print("Upload process has started for all documents.")
            return None

    def approve_documents(
        self,
        document_names: List[str],
        status: str,
        index_column: str = "document_name",
    ):
        client = MongoSingleton(self.mongodb_url)
        collection = client[self.mongodb_database][
            self.mongodb_collection_document_manager
        ]
        try:
            current_time = datetime.utcnow()
            status = status if status == "approved" else "unapproved"
            # 條件更新選擇
            if index_column == "document_name":
                """Approve documents by document names ('document_name').
                Change status from 'pending' to 'approved' and update current time in 'updated_at' .
                """
                result = collection.update_many(
                    {"document_name": {"$in": document_names}, "status": "pending"},
                    {"$set": {"status": status, "updated_at": current_time}},
                )

            elif index_column == "document_id":
                document_names = [ObjectId(doc_id) for doc_id in document_names]
                """Approve documents by document id ('document_id'). 
                Change status from 'pending' to 'approved' and update current time in 'updated_at' ."""
                result = collection.update_many(
                    {"_id": {"$in": document_names}, "status": "pending"},
                    {"$set": {"status": status, "updated_at": current_time}},
                )
            else:
                raise ValueError(
                    "Invalid doc_key. Please provide either 'document_name' or 'document_id'."
                )
            return result.modified_count
        except Exception as e:
            raise e

    def prepare_approved_document_infomation(self) -> List[Dict]:
        client = MongoSingleton(self.mongodb_url)
        collection = client[self.mongodb_database][
            self.mongodb_collection_document_manager
        ]

        try:
            result_cursor = collection.find({"status": "approved"})

            # Extracting required document IDs
            result = list(result_cursor)
            process_list = [doc["_id"] for doc in result]

            if process_list:
                modified_result = collection.update_many(
                    {"_id": {"$in": process_list}}, {"$set": {"status": "processing"}}
                )
                logging.info(
                    f"Update {modified_result.modified_count} documents' status to processing"
                )

                # Convert cursor to list after modifying status
                for doc in result:
                    doc["document_id"] = doc["_id"]
                    doc["document_name"] = doc.get("document_name")
                    doc["document_source"] = doc.get("source")
                return result
            else:
                return []

        except Exception as e:
            logging.error(f"Error in prepare_approved_document_infomation: {str(e)}")
            raise e

    def add_documents_to_vector_store(self, document_infomations: List[Dict]):
        client = MongoSingleton(self.mongodb_url)
        collection_vector = client[self.mongodb_database][
            self.mongodb_collection_vector
        ]
        collection_manager = client[self.mongodb_database][
            self.mongodb_collection_document_manager
        ]
        embedding_config = EbeddingConfig()
        model_config = embedding_config.get()
        embeddings = get_embedding_model(model_config=model_config)

        max_tokens_per_min = 180000
        current_tokens = 0
        for doc_info in tqdm(
            document_infomations, desc="Processing documents", unit="doc"
        ):
            try:
                doc_name, doc_id, doc_source = (
                    doc_info["document_name"],
                    ObjectId(doc_info["document_id"]),
                    doc_info["document_source"],
                )
                docs = get_storage_file(
                    container_name=self.storage_container_name,
                    document_name=doc_name,
                    connection_string=self.storage_connection_string,
                    chunk_size=self.document_chunk_size,
                    chunk_overlap=self.document_chunk_overlap,
                    separators=[" ", ",", "\n"],
                )

                filter_condition = {
                    "document_id": doc_id,
                    "document_name": doc_name,
                    "document_source": doc_source,
                }

                collection_vector.delete_many(filter_condition)
                for doc in docs:
                    if current_tokens > max_tokens_per_min:
                        time.sleep(60)
                        current_tokens = 0
                    doc.metadata["document_name"] = doc_name
                    doc.metadata["document_id"] = doc_id
                    doc.metadata["document_source"] = doc_source
                    doc.metadata["created_at"] = get_current_time(zone=self.timezone)

                    upload_file_to_vector_store(
                        documents=[doc],
                        collection=collection_vector,
                        collection_index=self.mongodb_collection_vector_special_index,
                        embeddings=embeddings,
                    )
                    current_tokens = current_tokens + count_token_number(
                        doc.page_content
                    )

                collection_manager.update_one(
                    {"_id": doc_id},
                    {
                        "$set": {
                            "status": "success",
                            "updated_at": get_current_time(zone=self.timezone),
                        }
                    },
                )
            except Exception as e:
                collection_manager.update_one(
                    {"_id": doc_id},
                    {
                        "$set": {
                            "status": "failed",
                            "updated_at": get_current_time(zone=self.timezone),
                        }
                    },
                )
                raise e
        return None

    def delete_documents_in_storage(self, document_names: List[str]):
        for doc_name in document_names:
            delete_storage_file(
                document_name=doc_name,
                container_name=self.storage_container_name,
                connection_string=self.storage_connection_string,
            )
        return None

    def delete_documents_in_vector_store(
        self, document_names: List[str], index_column: str = "document_id"
    ) -> int:
        client = MongoSingleton(self.mongodb_url)
        collection = client[self.mongodb_database][self.mongodb_collection_vector]
        deleted_count = 0
        try:
            result = collection.delete_many({index_column: {"$in": document_names}})
            deleted_count = result.deleted_count
            print(f"Deleted {deleted_count} documents.")
        except Exception as e:
            raise e
        return deleted_count

    def delete_documents(
        self, document_names: List[str], index_column: str = "document_name"
    ):
        client = MongoSingleton(self.mongodb_url)
        collection = client[self.mongodb_database][
            self.mongodb_collection_document_manager
        ]

        filter_condition = {}

        # If the index column is document_id, transform the provided strings into ObjectId instances.
        if index_column == "document_id":
            document_ids = [ObjectId(doc_id) for doc_id in document_names]
            filter_condition["_id"] = {"$in": document_ids}
            documents = collection.find(filter_condition)
            # update the document_names with the actual names from the DB
            document_names = [doc["document_name"] for doc in documents]
        else:
            filter_condition["document_name"] = {"$in": document_names}

        # Update status and timestamp in the database.
        collection.update_many(
            filter_condition,
            {
                "$set": {
                    "status": "deleted",
                    "updated_at": get_current_time(zone=self.timezone),
                }
            },
        )

        # Delete documents in storage and vector store.
        self.delete_documents_in_storage(document_names=document_names)
        # If the function is expected to work with ObjectIds, adjust the document_names accordingly
        if index_column == "document_id":
            document_names_for_vector_store = document_ids
        else:
            document_names_for_vector_store = document_names

        self.delete_documents_in_vector_store(
            document_names=document_names_for_vector_store, index_column=index_column
        )
        # Remove the documents from the database.
        result = collection.delete_many(filter_condition)
        return result.deleted_count

    def get_document_list(
        self,
        document_id: str = None,
        document_name: str = None,
        status: str = None,
        source: str = None,
        user_name: str = None,
        start_date: str = None,
        end_date: str = None,
        page_size: int = None,
        current_page: int = None,
        sorted_asc: bool = False,
        only_retain_contents: dict = None,
    ):
        client = MongoSingleton(self.mongodb_url)
        collection = client[self.mongodb_database][
            self.mongodb_collection_document_manager
        ]

        filter_condition = {}
        if only_retain_contents:
            for key, values in only_retain_contents.items():
                # Only add this condition if the key is NOT already present in filter_condition
                if key not in filter_condition:
                    filter_condition[key] = {"$in": values}

        total_documents = collection.count_documents(filter_condition)

        # Calculate total pages. If there are 50 documents and page_size is 10, then total_pages is 5
        if page_size:
            # Use ceil for rounding up
            total_pages = -(-total_documents // page_size)
        else:
            total_pages = 1

        if document_id:
            try:
                filter_condition["_id"] = ObjectId(document_id)
            except Exception:
                raise ValueError("Provided document_id is not a valid ObjectId string.")
        if document_name:
            regex_pattern = re.compile(f".*{document_name}.*", re.IGNORECASE)
            filter_condition["document_name"] = regex_pattern
        if status:
            filter_condition["status"] = status
        if source:
            filter_condition["source"] = source
        if user_name:
            regex_pattern = re.compile(f".*{user_name}.*", re.IGNORECASE)
            filter_condition["user_name"] = regex_pattern

        # Handle date filters
        if start_date or end_date:
            date_filter = {}
            if start_date:
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                date_filter["$gte"] = start_datetime
            if end_date:
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(
                    days=1
                )
                date_filter["$lt"] = end_datetime
            filter_condition["created_at"] = date_filter

        # First, get the total item count for the given conditions (before applying pagination)
        total_item_count = collection.count_documents(filter_condition)
        # Fetching documents with the given filter condition
        documents_cursor = collection.find(filter_condition)

        # Apply sorting
        sort_direction = 1 if sorted_asc else -1
        documents_cursor = documents_cursor.sort("created_at", sort_direction)

        # Convert current_page to skip (offset)

        current_page = current_page if current_page else 1
        skip = (current_page - 1) * page_size if page_size else 0

        # Apply page_size and skip
        if page_size:
            documents_cursor = documents_cursor.limit(page_size)
        if skip:
            documents_cursor = documents_cursor.skip(skip)

        # Convert cursor to list
        documents_list = list(documents_cursor)

        return {
            "documents": documents_list,
            "total_pages": total_pages,
            "current_page": current_page,
            "page_size": page_size,
            "total_item_count": total_item_count,
        }

    def get_distinct_list(self, column_name: str):
        try:
            client = MongoSingleton(self.mongodb_url)
            collection = client[self.mongodb_database][
                self.mongodb_collection_document_manager
            ]

            # Get distinct values for the given column
            distinct_values = collection.distinct(column_name)

            return distinct_values

        except Exception as e:
            # Handle any exception that might arise
            logging.error(f"Error getting distinct values for {column_name}: {str(e)}")
            return []

    def _refresh_collection_urls(self, collection, container_name):
        """
        A helper function to refresh URLs in a given collection.
        """
        # Count documents for the progress bar
        total_docs = collection.count_documents({})

        try:
            documents_cursor = collection.find({})

            for doc in tqdm(documents_cursor, total=total_docs, desc="Refreshing URLs"):
                try:
                    url = refresh_storage_document_url(
                        document_name=doc.get("document_name"),
                        container_name=container_name,
                        account_name=self.storage_account_name,
                        account_key=self.storage_account_key,
                        duration=self.duration,
                    )

                    # Update the MongoDB record with the new status, updated_at and the URL
                    collection.update_one(
                        {"_id": doc.get("_id")},
                        {
                            "$set": {
                                "updated_at": get_current_time(zone=self.timezone),
                                "url": url,
                            }
                        },
                    )
                except Exception as inner_e:
                    logging.error(
                        f"Error refreshing URL for document {doc.get('document_name')}: {str(inner_e)}"
                    )

        except PyMongoError as e:
            logging.error(f"MongoDB error during refresh: {str(e)}")
        except Exception as e:
            logging.error(f"Error during refresh: {str(e)}")

    def refresh_storage_documents_url(self):
        client = MongoSingleton(self.mongodb_url)

        # Refresh URLs for example_collection
        example_collection = client[self.mongodb_database][
            self.mongodb_collection_example
        ]
        self._refresh_collection_urls(
            collection=example_collection,
            container_name=self.storage_container_demo_name,
        )

        # Refresh URLs for collection
        collection = client[self.mongodb_database][
            self.mongodb_collection_document_manager
        ]
        self._refresh_collection_urls(
            collection=collection, container_name=self.storage_container_name
        )
