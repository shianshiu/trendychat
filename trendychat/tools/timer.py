'''
Author: Shawn
Date: 2023-09-25 18:42:36
LastEditTime: 2023-10-12 19:35:00
'''
import pytz
from datetime import datetime
import time


def timer_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} took {elapsed_time:.2f} seconds to run.")
        return result
    return wrapper


def get_current_time(zone='Asia/Taipei'):
    taiwan = pytz.timezone(zone)
    return datetime.now(taiwan).replace(tzinfo=None)
