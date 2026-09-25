import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from models.morphology import SwahiliLexicon
from schemas.morphology import (
    MorphologyAnalysisRequest,
    MorphologyAnalysisResponse,
    WordBreakdown
)
from services.morphology_engine import segment_verb, extract_lemma_and_intent, extract_stem

router = APIRouter()


@router.post("/analyze", response_model=MorphologyAnalysisResponse, summary="Analyze Kiswahili Morphology")
def analyze_morphology(
    req: MorphologyAnalysisRequest,
    db: Session = Depends(get_db)
) -> MorphologyAnalysisResponse:
    text = req.text.strip()
    tokens = re.findall(r"\w+", text)

    breakdowns = []
    for tok in tokens:
        seg = segment_verb(tok)
        root = seg.get("root") or tok

        # Find lexicon match if exists
        lex = db.query(SwahiliLexicon).filter(
            (SwahiliLexicon.root == root) | (SwahiliLexicon.canonical_lemma == tok.lower())
        ).first()
        if not lex:
            stem = extract_stem(tok)
            lex = db.query(SwahiliLexicon).filter(
                (SwahiliLexicon.root == stem) | (SwahiliLexicon.canonical_lemma == stem)
            ).first()

        wb = WordBreakdown(
            token=tok,
            root=lex.root if lex else root,
            canonical_lemma=lex.canonical_lemma if lex else None,
            part_of_speech=lex.part_of_speech if lex else ("kitendo" if seg.get("subject") else "jina"),
            segmentation=seg
        )
        breakdowns.append(wb)

    roots, intent_key = extract_lemma_and_intent(tokens, db)

    return MorphologyAnalysisResponse(
        input_text=text,
        tokens=tokens,
        breakdowns=breakdowns,
        inferred_intent=intent_key
    )
