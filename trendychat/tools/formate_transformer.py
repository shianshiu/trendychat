'''
Author: Shawn
Date: 2023-09-29 18:57:22
LastEditTime: 2023-09-29 19:58:53
'''

import json
from typing import Dict, Union

def doubleDict2string(content: Dict[str, Dict[str, Union[str, int, float]]]) -> Union[str, str]:
    """Convert parameters of type Dict[Dict] to a JSON string. 
    
    Since the parameters are lengthy and difficult to read, they are stored in a dict of dictionaries. 
    A function is used to convert them into a JSON string and print it out. 
    The resulting JSON string can then be copied to an environment variable.

    e.g,
    INPUT:
        params = {
            "jpe_20230905": {"unique_name":"jpe_20230905", "name":"TEST1", "region":"japan_east", "model":"text-embedding-ada-002"},
            "uke_20230905": {"name":"TEST1", "region":"uk_south",}
            }
        result = doubleDict2string(content=params)
    OUTPUT:
        {"jpe_20230905":{"name": "TEST1", "region": "japan_east", "model": "text-embedding-ada-002"}, "uke_20230905":{"name": "TEST1", "region": "uk_south"}}

    Args:
        content (Dict[Dict]): several parameters 。

    Returns:
        Union[str, str]: if input is valid, return JSON string. Otherwise, raise error message.
    """
    try:
        # 检查输入是否为字典，且字典中的每个值都是字典
        if not isinstance(content, dict) or not all(isinstance(value, dict) for value in content.values()):
            raise ValueError("Error: Input is not a dictionary of dictionaries.")

        # 使用 json.dumps 将字典转换为 JSON 字符串
        json_str = json.dumps(content)
        print(json_str)
        return json_str
    except Exception as e:
        # 如果转换过程中出现错误，返回一个清晰的错误消息
        raise ValueError(f"Error: An exception occurred - {str(e)}")

def json2parameters(content: str) -> Union[dict, str, int, list, float, bool]:
    """Check if the input is a valid JSON string, and convert it to a dictionary.
    
    Args:
        content (str): A JSON string.

    Returns:
        dict: The dictionary representation of the JSON string.
        str: If the input is not a valid JSON string, raise an error message.
    """
    try:
        # 尝试将输入的 JSON 字符串解析为字典
        parameters = json.loads(content)
        return parameters
    except json.JSONDecodeError as e:
        # 如果解析失败，返回一个错误消息
        raise ValueError(f"Error: Invalid JSON string - {str(e)}")



