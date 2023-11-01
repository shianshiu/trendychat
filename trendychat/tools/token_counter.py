'''
Author: Shawn
Date: 2023-10-11 14:18:42
LastEditTime: 2023-10-11 14:19:51
'''

import tiktoken


def count_token_number(
        string: str,
        encoding_name: str = "cl100k_base",
        model_name: str = "gpt-3.5-turbo"
) -> int:
    # import tiktoken
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
