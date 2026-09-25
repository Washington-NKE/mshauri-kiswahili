from typing import List
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base


class SwahiliLexicon(Base):
    __tablename__ = "swahili_lexicon"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    root: Mapped[str] = mapped_column(String(50), index=True)
    canonical_lemma: Mapped[str] = mapped_column(String(100), index=True)
    part_of_speech: Mapped[str] = mapped_column(String(50))
    english_intent: Mapped[str] = mapped_column(String(100), index=True)
    sample_surface_forms: Mapped[List[str]] = mapped_column(JSON, default=list)
