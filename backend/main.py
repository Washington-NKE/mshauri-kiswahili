import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.exceptions import DomainException, domain_exception_handler
from db.base import Base
from db.session import engine, fallback_to_sqlite, SessionLocal
from db.seed_data import seed_database
from api.v1.router import api_router

logger = logging.getLogger("mshauri.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler initializing DB tables with automatic fallback."""
    active_engine = engine
    try:
        Base.metadata.create_all(bind=active_engine)
        with SessionLocal() as session:
            seed_database(session)
    except Exception as e:
        logger.warning(f"Primary PostgreSQL database connection failed ({e}). Falling back to local SQLite.")
        active_engine = fallback_to_sqlite()
        Base.metadata.create_all(bind=active_engine)
        with SessionLocal() as session:
            seed_database(session)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Morphology-aware Kiswahili campus information retrieval assistant.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(DomainException, domain_exception_handler)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
def root():
    return {
        "message": "Karibu Mshauri Kiswahili API!",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs"
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
