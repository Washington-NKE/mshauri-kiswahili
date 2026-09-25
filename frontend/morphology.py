import re
from typing import List, Set, Dict

SWAHILI_STOP_WORDS: Set[str] = {
    "ninawezaje", "nawezaje", "ninaweza", "naweza", "nataka", "nitapata",
    "wapi", "vipi", "lini", "nani", "gani", "kuhusu", "kama", "au",
    "yangu", "yako", "zangu", "zako", "kwa", "ni", "na", "ya", "za", "wa", "cha", "vya",
    "kuna", "la", "je", "huu", "hii", "hiki", "hivi", "haya"
}


def normalize_swahili_noun(word: str) -> str:
    """Normalizes plural and locative Kiswahili nouns to canonical forms."""
    length_threshold = 4
    
    irregular_nouns: Dict[str, str] = {
        "wanafunzi": "mwanafunzi",
        "walimu": "mwalimu",
        "watu": "mtu",
        "wavulana": "mvulana",
        "wasichana": "msichana"
    }
    
    locative_nouns: Dict[str, str] = {
        "mtandaoni": "mtandao",
        "chuoni": "chuo",
        "ofisini": "ofisi",
        "shuleni": "shule",
        "madarasani": "darasa",
        "hostelini": "hosteli"
    }
    
    if word in irregular_nouns:
        return irregular_nouns[word]
        
    if word in locative_nouns:
        return locative_nouns[word]
    
    if len(word) > length_threshold:
        if word.startswith("mi"):
            return "m" + word[2:]
        elif word.startswith("vi"):
            return "ki" + word[2:]
        elif word.startswith("vy"):
            return "ch" + word[2:]
        elif word.startswith("ma"):
            return word[2:]
        elif word.startswith("u") and len(word) > 5:
            return word[1:]
            
    return word


def extract_swahili_root(word: str) -> str:
    """Extracts verbal root or normalized noun stem from Swahili token."""
    word = word.lower()
    word = re.sub(r'[^\w\s]', '', word)
    
    strict_exceptions: Set[str] = {
        "anakwaana", "miadi", "maji", "mali", "vile", "vyema", "makazi", "ushauri"
    }
    if word in strict_exceptions:
        return word
        
    # 1. Normalize Nouns
    word = normalize_swahili_noun(word)
    
    protected_nouns: Set[str] = {
        "mtandao", "chuo", "ofisi", "shule", "darasa", "hosteli", 
        "mwanafunzi", "mwalimu", "mtu", "mvulana", "msichana", "makazi", "ushauri"
    }
    if word in protected_nouns:
        return word
    
    # 2. Strip verb affixes (Subject + Tense)
    verb_prefix_pattern = r"^(ku)|^(ni|u|a|tu|m|wa|i|zi|ya|ki|vi)(na|li|ta|me|sipo)" 
    word = re.sub(verb_prefix_pattern, "", word)
    
    # 3. Strip interrogative suffix (-je)
    suffix_pattern = r"(je)$"
    word = re.sub(suffix_pattern, "", word)
    
    return word


def process_full_query(query: str) -> List[str]:
    """Preprocesses and extracts valid roots from full Swahili query string."""
    query = query.lower()
    query = query.replace("ana kwa ana", "anakwaana")
    
    clean_string = re.sub(r'[^\w\s]', ' ', query)
    words = clean_string.split()
    
    processed_roots: List[str] = []
    for word in words:
        if not word or word in SWAHILI_STOP_WORDS:
            continue
        root = extract_swahili_root(word)
        if root:
            processed_roots.append(root)
            
    return processed_roots