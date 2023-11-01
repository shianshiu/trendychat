'''
Author: Shawn
Date: 2023-10-04 17:01:51
LastEditTime: 2023-10-04 17:27:27
'''
import imghdr
import os
from typing import Union, Optional
from io import BytesIO, BufferedReader


def get_file_size_in_mb(file: Optional[Union[str, BufferedReader, BytesIO]]) -> float:
    """
    Get the size of a file or data object in MB.

    If `file` is a path to a file, return the size of the file in MB.
    If `file` is a data object (e.g., in-memory file), return the size of the data object in MB.

    # Usage
        file_path = "path_to_your_file.txt"
        size_in_mb = get_file_size_in_mb(file_path)
        print(f"The size of the file is {size_in_mb:.2f} MB")

    Args:
        file (Union[str, BufferedReader, BytesIO]): File path or data object.

    Returns:
        float: Size of the file or data object in MB.
    """

    # Check if file is a string path, then get its size
    if isinstance(file, str):
        file_size_in_bytes = os.path.getsize(file)
    # Check if file is a data object, then get its size
    elif isinstance(file, (BufferedReader, BytesIO)):
        file.seek(0, os.SEEK_END)  # Seek to the end
        file_size_in_bytes = file.tell()  # Get current file position (i.e., size)
        file.seek(0)  # Reset file position to the start
    else:
        raise TypeError(
            "Unsupported type for 'file'. Provide a file path or a data object.")

    # Convert bytes to MB
    file_size_in_mb = file_size_in_bytes / (1024 * 1024)

    return file_size_in_mb


def check_file_format(file: Optional[Union[str, BufferedReader, BytesIO]],
                      allowable_formats: Optional[list] = ['pdf']) -> bool:
    """
    Check if the file format of the given file is in the list of allowable formats.

    Args:
        file (Union[str, BufferedReader, BytesIO]): File path or data object.
        allowable_formats (list, optional): List of allowable file extensions (e.g., ['pdf', 'csv']). 

    Returns:
        bool: True if file format is allowable, False otherwise.
    """

    # If file is a string path, extract the file extension
    if isinstance(file, str):
        _, file_extension = os.path.splitext(file)
        # Strip the dot from the extension and convert to lowercase
        file_format = file_extension[1:].lower()
    # If file is a data object, attempt to determine its format
    elif isinstance(file, (BufferedReader, BytesIO)):
        file_format = imghdr.what(None, h=file.read())
        file.seek(0)  # Reset file position to the start
    else:
        raise TypeError(
            "Unsupported type for 'file'. Provide a file path or a data object.")

    # If allowable_formats is None, return True (as there are no restrictions)
    if allowable_formats is None:
        return True

    return file_format in allowable_formats
