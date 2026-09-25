import re
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.query import QueryRequest, QueryResponse
from schemas.document import CampusDocumentResponse
from services.morphology_engine import segment_verb, extract_lemma_and_intent
from services.retriever import retrieve_documents
from services.generator import synthesize_response

router = APIRouter()


@router.post("/", response_model=QueryResponse, summary="Process Swahili Query with Hybrid Retrieval")
def process_swahili_query(
    req: QueryRequest,
    db: Session = Depends(get_db)
) -> QueryResponse:
    raw_query = req.query.strip()

    # 1. Morphological segmentation of query tokens
    tokens = re.findall(r"\w+", raw_query.lower())
    token_breakdowns = []
    for tok in tokens:
        seg = segment_verb(tok)
        token_breakdowns.append({
            "token": tok,
            "segmentation": seg,
            "root": seg.get("root")
        })

    roots, intent_key = extract_lemma_and_intent(tokens, db)

    # 2. Hybrid document retrieval
    retrieved_docs = retrieve_documents(db, raw_query=raw_query, limit=3)
    grounding_doc = retrieved_docs[0] if retrieved_docs else None

    # 3. Gemini cross-lingual synthesis
    answer = synthesize_response(raw_query, grounding_doc)

    # Convert retrieved documents to Pydantic responses
    doc_responses = [CampusDocumentResponse.model_validate(d) for d in retrieved_docs]
    grounding_response = CampusDocumentResponse.model_validate(grounding_doc) if grounding_doc else None

    morphological_breakdown = {
        "tokens": tokens,
        "token_breakdowns": token_breakdowns,
        "extracted_roots": roots,
        "inferred_intent": intent_key
    }

    return QueryResponse(
        query=raw_query,
        answer_swahili=answer,
        morphological_breakdown=morphological_breakdown,
        grounding_source=grounding_response,
        retrieved_documents=doc_responses
    )
