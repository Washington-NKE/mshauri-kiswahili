from schemas.morphology import (
    VerbSegmentation,
    MorphologyAnalysisRequest,
    MorphologyAnalysisResponse,
    WordBreakdown,
)
from schemas.document import (
    CampusDocumentBase,
    CampusDocumentCreate,
    CampusDocumentResponse,
)
from schemas.query import QueryRequest, QueryResponse

__all__ = [
    "VerbSegmentation",
    "MorphologyAnalysisRequest",
    "MorphologyAnalysisResponse",
    "WordBreakdown",
    "CampusDocumentBase",
    "CampusDocumentCreate",
    "CampusDocumentResponse",
    "QueryRequest",
    "QueryResponse",
]
