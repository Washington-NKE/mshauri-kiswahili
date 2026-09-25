from fastapi import APIRouter
from api.v1.endpoints import query, morphology, grammar, documents

api_router = APIRouter()

api_router.include_router(query.router, prefix="/query", tags=["Query"])
api_router.include_router(morphology.router, prefix="/morphology", tags=["Morphology"])
api_router.include_router(grammar.router, prefix="/grammar", tags=["Grammar"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
