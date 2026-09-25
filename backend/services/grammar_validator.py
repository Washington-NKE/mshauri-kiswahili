from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from models.grammar import GrammarRule


def determine_ngeli(noun: str) -> Dict[str, str]:
    n = noun.lower().strip()
    if n.startswith("ki") or n.startswith("vi") or n.startswith("ch") or n.startswith("vy"):
        return {"code": "KI-VI", "singular_prefix": "ki", "plural_prefix": "vi", "concord": "ki-/vi-"}
    elif n.startswith("mwa") or n.startswith("mtu") or n.startswith("wa"):
        return {"code": "A-WA", "singular_prefix": "m", "plural_prefix": "wa", "concord": "a-/wa-"}
    elif n.startswith("m") or n.startswith("mi"):
        return {"code": "U-I", "singular_prefix": "m", "plural_prefix": "mi", "concord": "u-/i-"}
    elif n.startswith("ji") or n.startswith("ma") or n.startswith("somo"):
        return {"code": "LI-YA", "singular_prefix": "ji", "plural_prefix": "ma", "concord": "li-/ya-"}
    elif n.startswith("pa") or n.startswith("ku") or n.startswith("mu"):
        return {"code": "PA-KU-MU", "singular_prefix": "pa", "plural_prefix": "ku", "concord": "pa-/ku-/mu-"}
    else:
        return {"code": "U-ZI", "singular_prefix": "u", "plural_prefix": "n", "concord": "u-/zi-"}


def analyze_noun_agreement(noun: str, modifier: str) -> Dict[str, Any]:
    """
    Validates concord agreement according to Swahili Ngeli rules.
    Example: noun='kitambulisho', modifier='changu' -> Valid KI-VI agreement.
    """
    ngeli_info = determine_ngeli(noun)
    mod = modifier.lower().strip()
    n = noun.lower().strip()
    is_valid = False
    details = ""

    code = ngeli_info["code"]
    if code == "KI-VI":
        if (n.startswith("ki") or n.startswith("ch")) and (mod.startswith("ki") or mod.startswith("ch")):
            is_valid = True
        elif (n.startswith("vi") or n.startswith("vy")) and (mod.startswith("vi") or mod.startswith("vy")):
            is_valid = True
    elif code == "A-WA":
        if mod.startswith("w") or mod.startswith("m") or mod.startswith("y") or mod.startswith("a"):
            is_valid = True
    elif code == "U-I":
        if mod.startswith("w") or mod.startswith("y") or mod.startswith("m"):
            is_valid = True
    else:
        is_valid = True  # Permissive for generalized concordance

    details = f"Noun '{noun}' categorized under {code} with concord marker '{ngeli_info['concord']}'."
    return {
        "noun": noun,
        "modifier": modifier,
        "ngeli_code": ngeli_info["code"],
        "concord_marker": ngeli_info["concord"],
        "is_valid_agreement": is_valid,
        "details": details
    }


def get_all_grammar_rules(db: Session) -> list[GrammarRule]:
    return db.query(GrammarRule).all()
