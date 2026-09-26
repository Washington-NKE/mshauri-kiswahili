from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from schemas.document import CampusDocumentResponse


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        json_schema_extra={"example": "Ninawezaje kulipa ada ya shule kwa awamu?"},
        description="Kiswahili inquiry regarding campus policies"
    )

    @field_validator("query")
    @classmethod
    def strip_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query cannot be empty")
        return value


class QueryResponse(BaseModel):
    query: str
    answer_swahili: str
    morphological_breakdown: Dict[str, Any]
    grounding_source: Optional[CampusDocumentResponse] = None
    retrieved_documents: List[CampusDocumentResponse] = Field(default_factory=list)
