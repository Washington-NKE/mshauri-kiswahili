from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from schemas.document import CampusDocumentResponse


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        json_schema_extra={"example": "Ninawezaje kulipa ada ya shule kwa awamu?"},
        description="Kiswahili inquiry regarding campus policies"
    )


class QueryResponse(BaseModel):
    query: str
    answer_swahili: str
    morphological_breakdown: Dict[str, Any]
    grounding_source: Optional[CampusDocumentResponse] = None
    retrieved_documents: List[CampusDocumentResponse] = Field(default_factory=list)
