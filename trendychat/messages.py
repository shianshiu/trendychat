from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional


class ChatMessage(BaseModel):
    user_text: Optional[str] = None
    bot_text: Optional[str] = None
    user_timestamp: Optional[datetime] = None
    bot_timestamp: Optional[datetime] = None
    reference: List[dict] = []
    history: List[str] = []
    context: List[str] = []
    analysis_description: Optional[str] = None
    analysis_script: Optional[str] = None
    analysis_result: Optional[str] = None
