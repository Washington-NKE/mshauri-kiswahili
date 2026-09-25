from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class VerbSegmentation(BaseModel):
    subject: Optional[str] = Field(None, description="Subject prefix e.g. ni, u, a, wa")
    tense: Optional[str] = Field(None, description="Tense/Aspect marker e.g. na, li, ta, me, sipo")
    relative: Optional[str] = Field(None, description="Relative marker e.g. o, yo, cho")
    passive: Optional[str] = Field(None, description="Passive verb extension e.g. w")
    root: Optional[str] = Field(None, description="Extracted verbal root")
    suffix: Optional[str] = Field(None, description="Verbal suffix e.g. a, i, e")
    interrogative: Optional[str] = Field(None, description="Enclitic interrogative e.g. je, pi, ni")


class MorphologyAnalysisRequest(BaseModel):
    text: str = Field(
        ...,
        json_schema_extra={"example": "ninawezaje"},
        description="Kiswahili word or phrase to analyze"
    )


class WordBreakdown(BaseModel):
    token: str
    root: Optional[str] = None
    canonical_lemma: Optional[str] = None
    part_of_speech: Optional[str] = None
    segmentation: Dict[str, Any] = Field(default_factory=dict)


class MorphologyAnalysisResponse(BaseModel):
    input_text: str
    tokens: list[str]
    breakdowns: list[WordBreakdown]
    inferred_intent: Optional[str] = None
