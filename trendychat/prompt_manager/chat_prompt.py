"""
Author: Shawn
Date: 2023-09-12 16:05:25
LastEditors: Please set LastEditors
LastEditTime: 2023-09-25 21:11:59
FilePath: /SmartHelper_v1/trendychat/prompt_manager/chat_prompt.py
Description: 

Copyright (c) 2023 by ${git_name_email}, All Rights Reserved. 
"""


from typing import List
import os
from trendychat.tools.timer import timer_decorator

# from dotenv import load_dotenv
# load_dotenv()


@timer_decorator
def promt_function(
    context: List,
    version: str,
):
    """
    need run 'load_dotenv()'
    """
    nickname = os.getenv("REPRESENTATIVE_NAME")
    company = os.getenv("COMPANY_NAME")
    model_base = os.getenv("MODEL_BASE")
    direct_url = os.getenv("MODEL_BASE")
    if version == "v1":
        # 最簡短的說明
        ref = {
            "system": (
                f"Your name is {nickname}, an AI rep based on {model_base} from {company}. Refer to documents and provide concise answer with enthusiasm and emoticons. Direct to '{direct_url}' or relative URL if needed. No random replies."
            ),
            "assistant": "\n".join(
                [f"Doc {i+1}: {ctxt}" for i, ctxt in enumerate(context)]
            ),
        }
    elif version == "v2":
        # 這是現在DEMO用的
        ref = {
            "system": (
                f"""Your name is {nickname},and you are an AI customer service representative based on {model_base} from {company}. please refer to the reference and provide a response, the content of the response need to consider (1)if there's no corresponding answer,Especially for personnel information, ask for more specific information or guide students to the school's official website "{direct_url}" to find the information. please make sure not to provide random responses.(2)If there is a relevant answer, including the URL from the reference is important.Your responses should be lively and appropriately use various emoticons, but please keep them concise."""
            ),
            "assistant": "---" + "\n\n".join(["---\n\n" + ctxt for ctxt in context]),
        }
    elif version == "v3":
        # 較新的說明
        ref = {
            "system": (
                f"Your name is {nickname}. You are a {model_base} AI rep from {company}. For queries: \n\n"
                f"1.Without a direct answer, especially for personnel info, ask for details or direct to '{direct_url}'. No random replies.\n\n"
                f"2.If an answer exists and the reference document provides a URL, share it depending on the context.\n\n"
                f"3.Answer with enthusiasm and emoticons, but be concise.\n\n"
            ),
            "assistant": f"Based on my knowledge: {' '.join([f'From Document {i+1}: {ctxt}' for i, ctxt in enumerate(context)])} For more details, you can check out [{company}'s official website]({direct_url}). Hope this helps!",
        }
    elif version == "v4":
        # 這是最舊的

        ref = {
            "system": f"""You're an AI assistant of {company}, please refer to the reference and provide a response in JSON format only, like this: {{"confidence":"-1","answer":"尚未提供，請提供更多的細節"}} Here,(1)confidence: Indicates whether there is an ability to answer this time, divided into integer -1 for certain no, 0 for uncertain, and 1 for certain yes,(2)answer: The content of the response. If there's no corresponding answer, ask for more specific information. If there is a relevant answer, including the URL from the reference is important.""",
            "assistant": "---" + "\n\n".join(["---\n\n" + ctxt for ctxt in context]),
        }

    print("目前使用prompt的版本: ", version)
    return ref


class ChatPrompt:
    @classmethod
    def get_message(self, message: str, context: List[str]):
        prompt = promt_function(context=context, version="v2")

        return [
            {"role": "system", "content": prompt["system"]},
            {"role": "assistant", "content": prompt["assistant"]},
            {"role": "user", "content": message},
        ]


if __name__ == "__main__":
    context = []
    message = "請問東海大學的校長是誰？"
    Prompt = ChatPrompt()
    result = Prompt.get_message(message, context)
    breakpoint()
