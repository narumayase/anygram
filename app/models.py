from typing import Union
from pydantic import BaseModel

class Message(BaseModel):
    chat_id: Union[str, int]
    message_response: str