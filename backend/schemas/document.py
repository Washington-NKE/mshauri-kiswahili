from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class CampusDocumentBase(BaseModel):
    category: str
    intent_key: str
    title: str
    content_english: str
    content_swahili: Optional[str] = None
    keywords: List[str] = []


class CampusDocumentCreate(CampusDocumentBase):
    pass


class CampusDocumentResponse(CampusDocumentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
