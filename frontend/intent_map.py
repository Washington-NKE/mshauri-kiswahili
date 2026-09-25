# intent_map.py
# Entity and Action Intent Mapping for Kiswahili Campus Query Classifier

# 1. High-Priority Context Nouns (Entities) - Two-Pass Priority System
entity_intents = {
    "klabu": "clubs_and_societies",
    "shirika": "clubs_and_societies",
    "maelezo": "general_inquiry",
    "makazi": "hostel_allocation",
    "hosteli": "hostel_allocation",
    "hostel": "hostel_allocation",
    "afya": "health_services",
    "zahanati": "health_services",
    "ada": "tuition_fees",
    "karo": "tuition_fees",
    "cheti": "graduation_requirements",
    "shahada": "graduation_requirements",
    "nakala": "transcripts_request",
    "transkripti": "transcripts_request",
    "matokeo": "transcripts_request",
    "stakabadhi": "admissions",
    "kozi": "course_registration",
    "vitengo": "course_registration",
    "units": "course_registration",
    "ushauri": "academic_counseling",
    "miadi": "academic_counseling",
    "soma": "academics",
    "awamu": "tuition_fees",
    "fadhili": "scholarships",
    "ufadhili": "scholarships",
    "basari": "scholarships",
    "bursary": "scholarships",
    "kitambulisho": "student_id",
    "vitambulisho": "student_id",
    "ratiba": "exam_timetable",
    "mtihani": "exam_timetable",
    "mitihani": "exam_timetable",
    "mkopo": "student_loans",
    "mikopo": "student_loans",
    "helb": "student_loans",
    "maktaba": "library_services",
    "vitabu": "library_services",
    "wifi": "ict_portal",
    "mtandao": "ict_portal",
    "nywila": "ict_portal",
    "portal": "ict_portal",
    "michezo": "sports_recreation",
    "uwanja": "sports_recreation",
    "gym": "sports_recreation",
    "chakula": "catering_services",
    "mlo": "catering_services",
    "attachment": "industrial_attachment",
    "nyanjani": "industrial_attachment",
}

# 2. Low-Priority Verbs (Actions) - Fallback if no entity noun matches
action_intents = {
    "sajili": "course_registration",
    "jiunga": "admissions",
    "lipa": "tuition_fees",
    "fuzu": "graduation_requirements",
    "pata": "general_inquiry",
    "ahirisha": "deferment",
    "poteza": "student_id",
    "azima": "library_services",
    "omba": "scholarships",
}


def get_best_intent(roots_list: list) -> str:
    """
    Scans extracted roots using a two-pass priority system.
    Nouns override verbs to prevent intent collisions.
    """
    # Pass 1: High-priority context entity nouns
    for root in roots_list:
        clean_root = root.lower().strip()
        if clean_root in entity_intents and entity_intents[clean_root]:
            return entity_intents[clean_root]

    # Pass 2: Low-priority action verbs fallback
    for root in roots_list:
        clean_root = root.lower().strip()
        if clean_root in action_intents and action_intents[clean_root]:
            return action_intents[clean_root]

    return "general_inquiry"
