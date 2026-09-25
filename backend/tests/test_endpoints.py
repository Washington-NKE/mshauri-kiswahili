import pytest


def test_query_endpoint(client):
    payload = {"query": "Ninawezaje kulipa ada ya shule kwa awamu?"}
    response = client.post("/api/v1/query/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer_swahili" in data
    assert "morphological_breakdown" in data
    assert data["grounding_source"]["intent_key"] == "tuition_fees"


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
