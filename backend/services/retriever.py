import re
import unicodedata
from typing import List, Optional
from sqlalchemy.orm import Session
from models.document import CampusDocument
from services.morphology_engine import extract_lemma_and_intent


INTENT_KEYWORD_MAP = {
    "tuition_fees": ["ada", "malipo", "lipa", "awamu", "fee", "tuition", "instalment", "invoice", "receipt", "clearance"],
    "course_registration": ["sajili", "usajili", "vitengo", "kozi", "unit registration", "course registration", "add drop", "ongeza kitengo"],
    "exam_timetable": ["ratiba", "mtihani", "mitihani", "timetable", "schedule", "exam date"],
    "student_id": ["kitambulisho", "student id", "id card", "poteza id", "police abstract"],
    "graduation_requirements": ["fuzu", "uhitimu", "graduation", "clearance ya graduation", "shahada", "cheti cha graduation"],
    "student_loans": ["mkopo", "mikopo", "helb", "scholarship loan", "loan disbursement", "loan balance"],
    "scholarships": ["ufadhili", "bursary", "scholarship", "financial aid", "msaada wa karo"],
    "credit_transfer": ["credit transfer", "transfer credits", "hamisha credits", "exemptions", "course exemption"],
    "deferment": ["ahirisha", "kuahirisha", "likizo ya masomo", "deferment", "leave of absence"],
    "exam_card": ["exam card", "kadi ya mtihani", "exam entry", "ingia exam"],
    "hostel_allocation": ["hostel", "chumba", "vyumba", "booking", "accommodation", "room allocation", "makazi"],
    "off_campus_housing": ["off campus", "nyumba nje ya chuo", "private hostel", "accredited hostel"],
    "library_services": ["maktaba", "vitabu", "library", "azima", "faini ya kitabu", "e journal"],
    "health_services": ["afya", "zahanati", "hospitali", "medical", "clinic", "mgonjwa", "sick off", "counselling"],
    "disciplinary_policy": ["nidhamu", "disciplinary", "plagiarism", "udanganyifu", "cheating", "exam malpractice"],
    "industrial_attachment": ["attachment", "internship", "industrial training", "nyanjani", "logbook", "field placement"],
    "transcripts_request": ["transcript", "transkripti", "matokeo", "results slip", "statement of results"],
    "ict_portal": ["portal", "password", "nywila", "email ya chuo", "student email", "wifi", "wi fi", "internet", "ict helpdesk", "login"],
    "sports_recreation": ["michezo", "gym", "sports", "swimming pool", "bwawa", "recreation"],
    "international_students": ["visa", "pupil pass", "international student", "student pass", "bima ya afya"],
    "catering_services": ["chakula", "mlo", "cafeteria", "dining hall", "meal plan", "food"],
    "work_study": ["work study", "kazi chuoni", "part time job", "ajira ya muda", "student job"],
    "research_ethics": ["utafiti", "research ethics", "ethics approval", "IERC", "thesis approval"],
    "special_exams": ["supplementary", "special exam", "mitihani maalum", "resit", "retake", "marudio"],
    "security_emergency": ["usalama", "security", "dharura", "emergency", "lost property", "visitor pass"]
}

STOP_WORDS = {
    "na", "ya", "wa", "kwa", "ni", "je", "nini", "lini", "vipi", "gani",
    "the", "and", "for", "how", "what", "when", "where", "can", "do", "my",
    "i", "me", "to", "of", "is", "in", "a", "an", "please", "help",
    "student", "students", "mwanafunzi", "wanafunzi", "university", "chuo", "campus"
}
MIN_RETRIEVAL_SCORE = 4


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.findall(r"[\w]+", value))


def _score_document(query: str, tokens: set[str], doc: CampusDocument) -> int:
    title = _normalize(doc.title)
    keywords = [_normalize(word) for word in (doc.keywords or [])]
    swahili = _normalize(doc.content_swahili or "")
    english = _normalize(doc.content_english)
    score = 0

    for keyword in keywords:
        if keyword and re.search(rf"\b{re.escape(keyword)}\b", query):
            score += 5

    keyword_tokens = {word for keyword in keywords for word in keyword.split()}
    score += 4 * len(tokens & keyword_tokens)
    score += 2 * len(tokens & set(title.split()))
    score += 2 * len(tokens & set(swahili.split()))
    score += len(tokens & set(english.split()))
    return score


def detect_query_intent(query: str, db: Optional[Session] = None) -> Optional[str]:
    normalized = f" {_normalize(query)} "
    matched = [
        intent for intent, phrases in INTENT_KEYWORD_MAP.items()
        if any(f" {_normalize(phrase)} " in normalized for phrase in phrases)
    ]

    if db:
        tokens = re.findall(r"\w+", query.lower())
        _, inferred = extract_lemma_and_intent(tokens, db)
        if inferred in INTENT_KEYWORD_MAP:
            matched.append(inferred)

    return matched[0] if matched else None


def retrieve_documents(
    db: Session,
    raw_query: str,
    limit: int = 3,
    intent_key: Optional[str] = None,
) -> List[CampusDocument]:
    query = _normalize(raw_query)
    tokens = {token for token in query.split() if len(token) > 2 and token not in STOP_WORDS}
    if not query:
        return []

    detected_intent = (
        intent_key if intent_key in INTENT_KEYWORD_MAP
        else detect_query_intent(raw_query)
    )
    documents = db.query(CampusDocument).all()
    ranked = []
    for doc in documents:
        score = _score_document(query, tokens, doc)
        if doc.intent_key == detected_intent:
            score += 12
        if score >= MIN_RETRIEVAL_SCORE:
            ranked.append((score, doc))

    ranked.sort(key=lambda item: (-item[0], item[1].id))
    return [doc for _, doc in ranked[:max(1, limit)]]


def retrieve_document(db: Session, raw_query: str) -> Optional[CampusDocument]:
    docs = retrieve_documents(db, raw_query=raw_query, limit=1)
    return docs[0] if docs else None
