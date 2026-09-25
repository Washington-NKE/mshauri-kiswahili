from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base


class BenchmarkQuery(Base):
    __tablename__ = "benchmark_queries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    swahili_query: Mapped[str] = mapped_column(Text)
    english_translation: Mapped[str] = mapped_column(Text)
    target_intent: Mapped[str] = mapped_column(String(100), index=True)
    expected_document_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("campus_documents.id"), nullable=True
    )
