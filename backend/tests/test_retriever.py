import pytest
from services.retriever import retrieve_document, retrieve_documents


def test_retrieve_tuition_fees(db_session):
    doc = retrieve_document(db_session, "Ada inalipwaje muhula huu?")
    assert doc is not None
    assert doc.intent_key == "tuition_fees"


def test_retrieve_course_registration(db_session):
    doc = retrieve_document(db_session, "Nini kitatokea nisiposajili vitengo vyangu?")
    assert doc is not None
    assert doc.intent_key == "course_registration"


def test_retrieve_student_id(db_session):
    doc = retrieve_document(db_session, "Nimepoteza kitambulisho changu, nifanyeje?")
    assert doc is not None
    assert doc.intent_key == "student_id"


def test_retrieve_exam_timetable(db_session):
    doc = retrieve_document(db_session, "Ratiba ya mitihani itatoka lini?")
    assert doc is not None
    assert doc.intent_key == "exam_timetable"


def test_retrieve_multiple_documents(db_session):
    docs = retrieve_documents(db_session, "Ada na masomo", limit=3)
    assert len(docs) >= 1
