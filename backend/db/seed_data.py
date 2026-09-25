import sys
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from db.base import Base
from db.session import engine, SessionLocal
from models.document import CampusDocument
from models.morphology import SwahiliLexicon
from models.grammar import GrammarRule
from models.evaluation import BenchmarkQuery
from db.seeds.grammar_seeds import GRAMMAR_RULES_DATA
from db.seeds.lexicon_seeds import LEXICON_DATA
from db.seeds.document_seeds_part1 import DOCUMENT_SEEDS_PART1
from db.seeds.document_seeds_part2 import DOCUMENT_SEEDS_PART2


def seed_database(db: Session) -> None:
    print("Initializing database tables...")
    bind_engine = db.bind if db.bind else engine
    Base.metadata.create_all(bind=bind_engine)

    # 1. Seed Grammar Rules
    print("Seeding Grammar Rules (Ngeli & Affixes)...")
    for item in GRAMMAR_RULES_DATA:
        existing = db.query(GrammarRule).filter_by(code=item["code"]).first()
        if not existing:
            db.add(GrammarRule(**item))
    db.commit()

    # 2. Seed Swahili Lexicon
    print("Seeding Swahili Lexicon entries...")
    for item in LEXICON_DATA:
        existing = db.query(SwahiliLexicon).filter_by(
            root=item["root"], canonical_lemma=item["canonical_lemma"]
        ).first()
        if not existing:
            db.add(SwahiliLexicon(**item))
    db.commit()

    # 3. Seed Campus Documents
    print("Seeding Campus Policy Documents...")
    all_docs = DOCUMENT_SEEDS_PART1 + DOCUMENT_SEEDS_PART2
    for doc in all_docs:
        existing = db.query(CampusDocument).filter_by(intent_key=doc["intent_key"]).first()
        if not existing:
            c_doc = CampusDocument(**doc)
            db.add(c_doc)
    db.commit()

    # Update TSVector search_vector for PostgreSQL if available
    if bind_engine and bind_engine.dialect.name == "postgresql":
        print("Updating PostgreSQL TSVector search vectors...")
        db.execute(text("""
            UPDATE campus_documents
            SET search_vector = to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content_english, ''));
        """))
        db.commit()

    # 4. Seed Benchmark Queries
    print("Seeding Benchmark Queries...")
    benchmarks = [
        ("Ada inalipwaje muhula huu?", "How is tuition fee paid this semester?", "tuition_fees"),
        ("Nini kitatokea nisiposajili vitengo vyangu?", "What happens if I don't register my units?", "course_registration"),
        ("Nimepoteza kitambulisho changu, nifanyeje?", "I lost my ID card, what should I do?", "student_id"),
        ("Ratiba ya mitihani itatoka lini?", "When will the exam timetable be released?", "exam_timetable"),
        ("Ninawezaje kuomba mkopo wa HELB?", "How can I apply for HELB loan?", "student_loans")
    ]
    for sq, eq, intent in benchmarks:
        doc = db.query(CampusDocument).filter_by(intent_key=intent).first()
        existing = db.query(BenchmarkQuery).filter_by(swahili_query=sq).first()
        if not existing:
            db.add(BenchmarkQuery(
                swahili_query=sq,
                english_translation=eq,
                target_intent=intent,
                expected_document_id=doc.id if doc else None
            ))
    db.commit()
    print("Seeding completed successfully!")


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_database(session)
