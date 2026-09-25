import logging
from typing import Optional
from core.config import settings
from models.document import CampusDocument

logger = logging.getLogger("mshauri.generator")

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def synthesize_response(query: str, doc: Optional[CampusDocument]) -> str:
    """
    Synthesizes a Kiswahili Sanifu answer grounded on retrieved campus document.
    Uses google-genai SDK with gemini-2.5-flash model if GEMINI_API_KEY is set.
    """
    if not doc:
        return (
            "Kulingana na mfumo wa Mshauri Kiswahili, hakuna taarifa rasmi "
            "iliyopatikana kuhusu swali lako. Tafadhali tembelea ofisi ya msajili wa chuo."
        )

    doc_context = (
        f"Kichwa cha Sera: {doc.title}\n"
        f"Maelezo ya Kiingereza: {doc.content_english}\n"
        f"Maelezo ya Kiswahili: {doc.content_swahili or ''}"
    )

    prompt = (
        "Wewe ni Mshauri Kiswahili, msaidizi rasmi wa taaluma na sera za chuo kikuu.\n"
        "Jibu swali la mwanafunzi kikamilifu kwa Kiswahili Sanifu kilicho na sarufi sahihi.\n"
        "Tumia vipengele vya orodha (bullet points) kwa taratibu za hatua kwa hatua.\n"
        "HAKIKISHA majibu yako yanategemea Sera Rasmi ifuatayo TU. Usiongeze sheria za kufikirika.\n\n"
        f"--- SERA RASMI YA CHUO ---\n{doc_context}\n-----------------------\n\n"
        f"Swali la Mwanafunzi: {query}\n"
        "Jibu (kwa Kiswahili Sanifu):"
    )

    if settings.GEMINI_API_KEY and GENAI_AVAILABLE:
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}. Falling back to rule-based synthesis.")

    # Rule-based fallback synthesis grounded on retrieved document
    sw_text = doc.content_swahili or doc.content_english
    return (
        f"Kulingana na sera ya chuo kuhusu **{doc.title}**:\n\n"
        f"• {sw_text}\n\n"
        f"• Kategoria ya Huduma: {doc.category.upper()}\n"
        f"• Kumbukumbu ya Sera: {doc.intent_key}\n"
        f"Kwa maelezo zaidi, tembelea portal ya mwanafunzi au ofisi husika."
    )
