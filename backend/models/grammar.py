from typing import Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base


class GrammarRule(Base):
    __tablename__ = "grammar_rules"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rule_type: Mapped[str] = mapped_column(String(50), index=True)
    code: Mapped[str] = mapped_column(String(50), index=True)
    prefix_singular: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    prefix_plural: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    concord_marker: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    description: Mapped[str] = mapped_column(Text)
