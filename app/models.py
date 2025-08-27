from typing import Union, Optional
from pydantic import BaseModel

class Message(BaseModel):
    chat_id: Optional[Union[str, int]] = None
    text: str
