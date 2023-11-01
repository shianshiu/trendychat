"""
Author: Shawn
Date: 2023-10-12 09:58:21
LastEditTime: 2023-10-12 16:37:24
"""
from trendychat.chain.simple_chat import SimpleChat


message = "東海校長是誰？"
print(f"Q.{message}")
print("=" * 40)
chat = SimpleChat()
ans = chat.reply(message=message)
print("=" * 40)
print(f"A.{ans}")
breakpoint()
