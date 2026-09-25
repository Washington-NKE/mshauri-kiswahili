import re
from typing import List, Optional
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session
from models.document import CampusDocument
from services.morphology_engine import extract_lemma_and_intent, segment_verb, extract_stem


INTENT_KEYWORD_MAP = {
    "tuition_fees": ["ada", "lipa", "awamu", "tuition", "fee", "60/40", "instalment"],
    "course_registration": ["sajili", "usajili", "vitengo", "kozi", "registration", "units"],
    "exam_timetable": ["ratiba", "mtihani", "mitihani", "timetable", "schedule", "exam"],
    "student_id": ["kitambulisho", "vitambulisho", "id", "card", "poteza", "abstract"],
    "graduation_requirements": ["fuzu", "uhitimu", "cheti", "shahada", "graduation", "clearance"],
    "student_loans": ["mkopo", "mikopo", "helb", "loan", "bodi"],
    "scholarships": ["ufadhili", "bursary", "scholarship", "maombi", "fadhiliwa"],
    "deferment": ["ahirisha", "kuahirisha", "likizo", "deferment", "leave"],
    "hostel_allocation": ["hostel", "chumba", "vyumba", "booking", "accommodation"],
    "library_services": ["maktaba", "vitabu", "library", "azima", "faini"],
    "health_services": ["afya", "zahanati", "hospitali", "health", "medical"]
}


def detect_query_intent(query: str, db: Optional[Session] = None) -> Optional[str]:
    q_lower = query.lower()
    tokens = re.findall(r"\w+", q_lower)

    # 1. Direct morphological/lexicon lookup
    roots, inferred = extract_lemma_and_intent(tokens, db)
    if inferred and inferred != "general_inquiry":
        return inferred

    # 2. Keyword mapping check
    for intent, kw_list in INTENT_KEYWORD_MAP.items():
        for kw in kw_list:
            if kw in q_lower:
                return intent
            for t in tokens:
                stem = extract_stem(t)
                if stem in kw or kw in stem:
                    return intent
    return None


def retrieve_documents(db: Session, raw_query: str, limit: int = 3) -> List[CampusDocument]:
    detected_intent = detect_query_intent(raw_query, db)

    # Tier 1: Exact Intent Match
    if detected_intent:
        doc = db.query(CampusDocument).filter(CampusDocument.intent_key == detected_intent).first()
        if doc:
            other_docs = db.query(CampusDocument).filter(
                CampusDocument.intent_key != detected_intent
            ).limit(limit - 1).all()
            return [doc] + other_docs

    # Tier 2: Keyword / Full-Text Search Fallback
    tokens = re.findall(r"\w+", raw_query.lower())
    clean_terms = [t for t in tokens if len(t) > 2]

    # Full text search in PostgreSQL if available
    if db.bind and db.bind.dialect.name == "postgresql" and clean_terms:
        ts_query_str = " | ".join(clean_terms)
        results = db.query(CampusDocument).filter(
            CampusDocument.search_vector.op("@@")(func.to_tsquery("english", ts_query_str))
        ).limit(limit).all()
        if results:
            return results

    # Fallback ILIKE matching
    conditions = []
    for term in clean_terms:
        conditions.append(CampusDocument.title.ilike(f"%{term}%"))
        conditions.append(CampusDocument.content_english.ilike(f"%{term}%"))
        conditions.append(CampusDocument.content_swahili.ilike(f"%{term}%"))

    if conditions:
        results = db.query(CampusDocument).filter(or_(*conditions)).limit(limit).all()
        if results:
            return results

    # Ultimate fallback: return first documents
    return db.query(CampusDocument).limit(limit).all()


def retrieve_document(db: Session, raw_query: str) -> Optional[CampusDocument]:
    docs = retrieve_documents(db, raw_query=raw_query, limit=1)
    return docs[0] if docs else None
