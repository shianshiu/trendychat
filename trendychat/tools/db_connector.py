'''
Author: Shawn
Date: 2023-09-29 20:23:19
LastEditTime: 2023-10-05 18:52:36
'''
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import threading

load_dotenv()
mongodb_url = os.getenv("MONGODB_URI")


class MongoSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, url=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MongoSingleton, cls).__new__(cls)
                # 如果提供了 url，則使用該 url 建立連接
                # 否則從環境變數中獲取 url
                connect_url = url if url else mongodb_url
                cls._instance.client = MongoClient(connect_url)
        return cls._instance

    def get_connection(self):
        with self._lock:
            try:
                # 嘗試做一個簡單的操作以確定連接仍然健康
                self._instance.client.admin.command('ping')
            except ConnectionFailure:
                # 如果連接失效，則重新建立連接
                self._instance.client = MongoClient(mongodb_url)
        return self._instance.client

    # 加入此方法以支持索引訪問
    def __getitem__(self, key):
        return self.get_connection()[key]


if __name__ == "__main__":

    # 使用方式：
    db_name = os.getenv("MONGODB_DATABASE_NANE")
    mongo_instance = MongoSingleton()
    # print(mongo_instance[db_name])  # 這將顯示你的數據庫對象

    another_instance = MongoSingleton()
    # print(another_instance[db_name])  # 這將顯示相同的數據庫對象，確認我們的 Singleton 實現是正確的

    if id(mongo_instance) == id(another_instance):
        print("mongo_instance1 and mongo_instance2 are the same instance.")
    else:
        print("They are different instances.")
