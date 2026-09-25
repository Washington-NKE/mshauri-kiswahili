from typing import List, Optional
from sqlalchemy import String, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import TSVECTOR
from db.base import Base


class CampusDocument(Base):
    __tablename__ = "campus_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    intent_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    content_english: Mapped[str] = mapped_column(Text)
    content_swahili: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords: Mapped[List[str]] = mapped_column(JSON, default=list)
    search_vector: Mapped[Optional[str]] = mapped_column(
        TSVECTOR().with_variant(Text, "sqlite"), nullable=True
    )

    __table_args__ = (
        Index(
            "idx_campus_docs_search_vector",
            "search_vector",
            postgresql_using="gin",
        ),
    )
