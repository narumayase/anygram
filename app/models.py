from typing import Union
from pydantic import BaseModel

class TelegramMessage(BaseModel):
    chat_id: Union[str, int]
    text: str