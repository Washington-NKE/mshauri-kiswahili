import re
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
from models.morphology import SwahiliLexicon

SUBJECT_PREFIXES = ["ni", "u", "a", "tu", "m", "wa", "ki", "vi", "li", "ya", "zi", "i", "pa", "ku", "mu"]
TENSE_MARKERS = ["sipo", "na", "li", "ta", "me", "ki", "hu", "ka", "n"]
RELATIVE_MARKERS = ["o", "ye", "cho", "vyo", "lo", "yo", "zo", "po", "ko", "mo"]
INTERROGATIVES = ["je", "pi", "ni"]


def segment_verb(word: str) -> Dict[str, Any]:
    w = word.lower().strip()
    res = {
        "subject": None,
        "tense": None,
        "relative": None,
        "passive": None,
        "root": None,
        "suffix": None,
        "interrogative": None
    }
    
    # 1. Check interrogative enclitic at end (e.g. -je, -pi, -ni)
    for inter in INTERROGATIVES:
        if w.endswith(inter) and len(w) > len(inter) + 3:
            res["interrogative"] = inter
            w = w[:-len(inter)]
            break

    # 2. Check subject prefix at start
    matched_subj = None
    for subj in sorted(SUBJECT_PREFIXES, key=len, reverse=True):
        if w.startswith(subj):
            matched_subj = subj
            break

    if matched_subj:
        res["subject"] = matched_subj
        w_after_subj = w[len(matched_subj):]

        # 3. Check tense marker
        matched_tense = None
        for tense in sorted(TENSE_MARKERS, key=len, reverse=True):
            if w_after_subj.startswith(tense):
                matched_tense = tense
                break

        if matched_tense:
            res["tense"] = matched_tense
            w_after_tense = w_after_subj[len(matched_tense):]

            # 4. Check relative marker (e.g. walio-soma -> rel 'o')
            matched_rel = None
            for rel in sorted(RELATIVE_MARKERS, key=len, reverse=True):
                if w_after_tense.startswith(rel) and len(w_after_tense) > len(rel) + 2:
                    matched_rel = rel
                    break

            if matched_rel:
                res["relative"] = matched_rel
                w_stem = w_after_tense[len(matched_rel):]
            else:
                w_stem = w_after_tense

            # 5. Check passive marker 'w' or 'wa' near end (e.g. unalipwaje -> lip + w + a)
            if len(w_stem) >= 3 and w_stem.endswith("wa"):
                res["passive"] = "w"
                res["suffix"] = "a"
                res["root"] = w_stem[:-2]
            elif len(w_stem) >= 3 and w_stem[-2:] in ["wa", "wi", "we"]:
                res["passive"] = "w"
                res["suffix"] = w_stem[-1]
                res["root"] = w_stem[:-2]
            elif len(w_stem) >= 2:
                res["suffix"] = w_stem[-1]
                res["root"] = w_stem[:-1]
            else:
                res["root"] = w_stem
            return res

    # Fallback root extraction
    res["root"] = w
    return res


def extract_stem(word: str) -> str:
    """Strips common noun/verb prefixes to isolate root."""
    w = word.lower().strip()
    for p in ["kitambulisho", "vitambulisho"]:
        if w == p:
            return "tambulisisho"
    for p in ["mtihani", "mitihani"]:
        if p in w:
            return "tihani"
    for prefix in ["ku", "ki", "vi", "m", "wa", "mi", "ma", "u", "n"]:
        if w.startswith(prefix) and len(w) > len(prefix) + 2:
            w = w[len(prefix):]
            break
    return w


def extract_lemma_and_intent(
    tokens: List[str], db: Optional[Session] = None
) -> Tuple[List[str], str]:
    roots = []
    found_intents = []

    for token in tokens:
        clean_tok = re.sub(r"[^\w\s]", "", token.lower().strip())
        if not clean_tok:
            continue
        seg = segment_verb(clean_tok)
        root = seg.get("root") or clean_tok
        roots.append(root)

        # Database lookup for lexicon entry
        if db:
            lex = db.query(SwahiliLexicon).filter(
                (SwahiliLexicon.root == root) | (SwahiliLexicon.canonical_lemma == clean_tok)
            ).first()
            if not lex:
                # Try stem fallback
                stem = extract_stem(clean_tok)
                lex = db.query(SwahiliLexicon).filter(
                    (SwahiliLexicon.root == stem) | (SwahiliLexicon.canonical_lemma == stem)
                ).first()
            if lex and lex.english_intent:
                found_intents.append(lex.english_intent)

    # Prioritize specific intents over generic 'academics'
    specific_intents = [i for i in found_intents if i != "academics"]
    primary_intent = (
        specific_intents[0] if specific_intents
        else (found_intents[0] if found_intents else "general_inquiry")
    )
    return roots, primary_intent
