'''
Author: Shawn
Date: 2023-09-25 17:01:57
LastEditTime: 2023-09-29 20:57:50
'''
# from pymongo.errors import ConnectionFailure
# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os

# load_dotenv()
# MongodbURI = os.getenv("MONGODB_URI")
# dbName = os.getenv("dbName")


# class MongoSingleton:
#     _instance = None

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(MongoSingleton, cls).__new__(cls)
#             cls._instance.client = MongoClient(MongodbURI)
#         return cls._instance

#     def get_connection(self):
#         try:
#             # 嘗試做一個簡單的操作以確定連接仍然健康
#             self._instance.client.admin.command('ping')
#         except ConnectionFailure:
#             # 如果連接失效，則重新建立連接
#             self._instance.client = MongoClient(MongodbURI)
#         return self._instance.client

#     # 加入此方法以支持索引訪問
#     def __getitem__(self, key):
#         return self.get_connection()[key]
