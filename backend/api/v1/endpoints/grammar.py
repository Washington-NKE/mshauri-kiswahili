from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.session import get_db
from models.grammar import GrammarRule
from services.grammar_validator import analyze_noun_agreement, get_all_grammar_rules

router = APIRouter()


@router.get("/rules", summary="List All Active Grammatical Rules and Noun Classes")
def list_grammar_rules(
    rule_type: str = Query(None, description="Filter by rule_type (e.g. ngeli, kiambishi_awali, njeo)"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    query = db.query(GrammarRule)
    if rule_type:
        query = query.filter(GrammarRule.rule_type == rule_type)
    rules = query.all()
    return [
        {
            "id": r.id,
            "rule_type": r.rule_type,
            "code": r.code,
            "prefix_singular": r.prefix_singular,
            "prefix_plural": r.prefix_plural,
            "concord_marker": r.concord_marker,
            "description": r.description
        }
        for r in rules
    ]


@router.get("/agreement", summary="Verify Noun-Modifier Concordance Agreement")
def verify_agreement(
    noun: str = Query(..., examples=["kitambulisho"]),
    modifier: str = Query(..., examples=["changu"])
) -> Dict[str, Any]:
    return analyze_noun_agreement(noun, modifier)
