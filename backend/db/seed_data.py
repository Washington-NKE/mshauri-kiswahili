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
    existing_rule_codes = {r[0] for r in db.query(GrammarRule.code).all()}
    new_rules = [GrammarRule(**item) for item in GRAMMAR_RULES_DATA if item["code"] not in existing_rule_codes]
    if new_rules:
        db.bulk_save_objects(new_rules)
        db.commit()

    # 2. Seed Swahili Lexicon
    print("Seeding Swahili Lexicon entries...")
    existing_lexicon = {(l[0], l[1]) for l in db.query(SwahiliLexicon.root, SwahiliLexicon.canonical_lemma).all()}
    new_lexicon = [
        SwahiliLexicon(**item) for item in LEXICON_DATA
        if (item["root"], item["canonical_lemma"]) not in existing_lexicon
    ]
    if new_lexicon:
        db.bulk_save_objects(new_lexicon)
        db.commit()

    # 3. Seed Campus Documents
    print("Seeding Campus Policy Documents...")
    all_docs = DOCUMENT_SEEDS_PART1 + DOCUMENT_SEEDS_PART2
    existing_doc_intents = {d[0] for d in db.query(CampusDocument.intent_key).all()}
    new_docs = [CampusDocument(**doc) for doc in all_docs if doc["intent_key"] not in existing_doc_intents]
    if new_docs:
        db.bulk_save_objects(new_docs)
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
    existing_benchmarks = {b[0] for b in db.query(BenchmarkQuery.swahili_query).all()}
    doc_map = {d[0]: d[1] for d in db.query(CampusDocument.intent_key, CampusDocument.id).all()}
    new_benchmarks = []
    for sq, eq, intent in benchmarks:
        if sq not in existing_benchmarks:
            new_benchmarks.append(BenchmarkQuery(
                swahili_query=sq,
                english_translation=eq,
                target_intent=intent,
                expected_document_id=doc_map.get(intent)
            ))
    if new_benchmarks:
        db.bulk_save_objects(new_benchmarks)
        db.commit()
    print("Seeding completed successfully!")


if __name__ == "__main__":
    with SessionLocal() as session:
        seed_database(session)
