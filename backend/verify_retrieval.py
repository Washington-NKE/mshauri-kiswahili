from db.session import SessionLocal
from db.seed_data import seed_database
from services.retriever import retrieve_document

test_queries = [
    # Complex agglutinated query -> Expected intent: tuition_fees
    ("Ada inalipwaje muhula huu?", "tuition_fees"),
    # Negative conditional -> Expected intent: course_registration
    ("Nini kitatokea nisiposajili vitengo vyangu?", "course_registration"),
    # Locative query -> Expected intent: student_id
    ("Nimepoteza kitambulisho changu, nifanyeje?", "student_id"),
    # Timetable query -> Expected intent: exam_timetable
    ("Ratiba ya mitihani itatoka lini?", "exam_timetable"),
]

print("--- AUDITING RETRIEVAL PIPELINE ---")
with SessionLocal() as db:
    seed_database(db)
    for query_text, expected_intent in test_queries:
        doc = retrieve_document(db, raw_query=query_text)
        assert doc is not None, f"Failed to retrieve document for '{query_text}'"
        print(f"\nQuery: '{query_text}'")
        print(f"Matched Document: [{doc.category}] {doc.title} (Intent: {doc.intent_key})")
        assert doc.intent_key == expected_intent, f"Wrong intent: Expected {expected_intent}, got {doc.intent_key}"

print("\nRetrieval precision verification complete!")
