import pytest


def test_query_endpoint(client):
    payload = {"query": "Ninawezaje kulipa ada ya shule kwa awamu?"}
    response = client.post("/api/v1/query/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer_swahili" in data
    assert "morphological_breakdown" in data
    assert data["grounding_source"]["intent_key"] == "tuition_fees"


def test_exam_timetable_sample_matches_policy(client):
    response = client.post(
        "/api/v1/query/", json={"query": "Ratiba ya mitihani itatoka lini?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["morphological_breakdown"]["inferred_intent"] == "exam_timetable"
    assert data["grounding_source"]["intent_key"] == "exam_timetable"


def test_unrecognized_question_is_not_grounded_in_an_unrelated_policy(client):
    response = client.post(
        "/api/v1/query/", json={"query": "Where can I check today's weather?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grounding_source"] is None
    assert data["retrieved_documents"] == []
    assert "Sina taarifa rasmi" in data["answer_swahili"]


def test_blank_query_is_rejected(client):
    response = client.post("/api/v1/query/", json={"query": "   "})
    assert response.status_code == 422


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_morphology_analyze_endpoint(client):
    payload = {"text": "ninawezaje"}
    response = client.post("/api/v1/morphology/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["input_text"] == "ninawezaje"
    assert len(data["breakdowns"]) >= 1
    assert data["breakdowns"][0]["token"] == "ninawezaje"


def test_grammar_rules_endpoint(client):
    response = client.get("/api/v1/grammar/rules")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    codes = [r["code"] for r in data]
    assert "A-WA" in codes
    assert "KI-VI" in codes


def test_documents_endpoint(client):
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
