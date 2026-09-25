from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from db.session import get_db
from models.document import CampusDocument
from schemas.document import CampusDocumentResponse

router = APIRouter()


@router.get("/", response_model=List[CampusDocumentResponse], summary="List Campus Policy Documents")
def list_documents(
    category: str = Query(None, description="Filter by category (e.g. finance, academics, housing)"),
    search: str = Query(None, description="Filter documents by search term"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> List[CampusDocumentResponse]:
    query = db.query(CampusDocument)
    if category:
        query = query.filter(CampusDocument.category == category)
    if search:
        s_term = f"%{search}%"
        query = query.filter(
            (CampusDocument.title.ilike(s_term)) | (CampusDocument.content_english.ilike(s_term))
        )
    docs = query.offset(skip).limit(limit).all()
    return [CampusDocumentResponse.model_validate(d) for d in docs]


@router.get("/{doc_id}", response_model=CampusDocumentResponse, summary="Get Document Details by ID")
def get_document(
    doc_id: int,
    db: Session = Depends(get_db)
) -> CampusDocumentResponse:
    doc = db.query(CampusDocument).filter(CampusDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campus document with ID {doc_id} not found."
        )
    return CampusDocumentResponse.model_validate(doc)
