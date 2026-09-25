import pytest
from services.morphology_engine import segment_verb, extract_lemma_and_intent, extract_stem


def test_segment_verb_ninawezaje():
    res = segment_verb("ninawezaje")
    assert res["subject"] == "ni"
    assert res["tense"] == "na"
    assert res["root"] == "wez"
    assert res["interrogative"] == "je"


def test_segment_verb_waliosoma():
    res = segment_verb("waliosoma")
    assert res["subject"] == "wa"
    assert res["tense"] == "li"
    assert res["relative"] == "o"
    assert res["root"] == "som"


def test_segment_verb_nisiposajili():
    res = segment_verb("nisiposajili")
    assert res["subject"] == "ni"
    assert res["tense"] == "sipo"
    assert res["root"] == "sajil"


def test_segment_verb_unalipwaje():
    res = segment_verb("unalipwaje")
    assert res["subject"] == "u"
    assert res["tense"] == "na"
    assert res["root"] == "lip"
    assert res["passive"] == "w"
    assert res["interrogative"] == "je"


def test_extract_stem_and_intent(db_session):
    tokens = ["ninawezaje", "kulipa", "ada"]
    roots, intent = extract_lemma_and_intent(tokens, db_session)
    assert "wez" in roots or "lip" in roots
    assert intent == "tuition_fees"
