'''
Author: Shawn
Date: 2023-10-12 11:26:05
LastEditTime: 2023-10-12 11:28:56
'''
import os


def list_files_in_directory(directory: str) -> list:
    """指定路徑下的資料夾，回傳所有的檔案路徑

    Args:
        directory_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        file_paths = []  # 儲存所有檔案的路徑
        items = os.listdir(directory)

        for item in items:
            if item == ".DS_Store":
                continue

            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                file_paths.append(item_path)  # 將檔案的完整路徑加入列表
            elif os.path.isdir(item_path):
                file_paths.extend(list_files_in_directory(
                    item_path))  # 遞迴處理子目錄並合併列表
        return file_paths  # 回傳所有檔案的完整路徑列表
    except Exception as e:
        print("發生錯誤:", str(e))
        return []
