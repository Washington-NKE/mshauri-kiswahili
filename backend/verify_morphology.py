from services.morphology_engine import segment_verb, extract_lemma_and_intent

test_cases = [
    ("ninawezaje", {"subject": "ni", "tense": "na", "root": "wez", "interrogative": "je"}),
    ("waliosoma", {"subject": "wa", "tense": "li", "relative": "o", "root": "som"}),
    ("nisiposajili", {"subject": "ni", "tense": "sipo", "root": "sajil"}),
    ("unalipwaje", {"subject": "u", "tense": "na", "root": "lip", "passive": "w", "interrogative": "je"}),
]

print("--- AUDITING KISWAHILI MORPHOLOGY ENGINE ---")
for word, expected in test_cases:
    result = segment_verb(word)
    print(f"\nTarget: {word}")
    print(f"Result: {result}")
    for k, v in expected.items():
        assert result.get(k) == v, f"Mismatch for '{k}': expected '{v}', got '{result.get(k)}'"

print("\nAll verb segmentations passed linguistic verification!")
