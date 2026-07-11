from pydantic import BaseModel
from typing import Optional


class KnowledgeItem(BaseModel):
    type: str
    title: str
    content: str
    source: Optional[str] = None

