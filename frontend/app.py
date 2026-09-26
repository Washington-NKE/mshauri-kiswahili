import os
import requests
import streamlit as st
from morphology import process_full_query
from intent_map import get_best_intent

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000/api/v1/query/")

st.set_page_config(
    page_title="Mshauri wa Kiswahili 🇰🇪",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6, #06b6d4);
        color: white; border: none; border-radius: 8px; font-weight: 600;
    }
    .badge-pill {
        background: rgba(16, 185, 129, 0.15); border: 1px solid #10b981;
        color: #10b981; padding: 4px 12px; border-radius: 20px; font-size: 12px;
    }
    .card-box {
        background-color: #1e293b; border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px; padding: 18px; margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation Mode Switcher
st.sidebar.image("https://img.icons8.com/isometric/100/scroll.png", width=64)
st.sidebar.title("Mshauri wa Kiswahili")
st.sidebar.caption("Msaidizi wa masomo na huduma za chuo kikuu")

view_mode = st.sidebar.radio(
    "Chagua mwonekano:",
    [
        "Mwonekano wa mwanafunzi",
        "Mwonekano wa majaribio ya mfumo"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Maswali ya mfano:**")
sample_queries = [
    "Ninawezaje kulipa ada ya shule kwa awamu?",
    "Nini kitatokea nisiposajili vitengo vyangu?",
    "Nimepoteza kitambulisho changu, nifanyeje?",
    "Ratiba ya mitihani itatoka lini?",
    "Ninawezaje kuomba mkopo wa HELB?",
    "Je, ninawezaje kufuga kuku au wanyama kwenye bweni la chuo? (⚠️ Fallback Demo)"
]
selected_sample = st.sidebar.selectbox("Chagua swali la mfano:", ["Andika swali lako mwenyewe"] + sample_queries)

# Clean selected sample text if tag present
clean_selected_sample = selected_sample.split(" (⚠️")[0] if selected_sample != "Andika swali lako mwenyewe" else ""

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []


# Function to Query Backend API
def query_backend(user_text: str):
    try:
        resp = requests.post(API_ENDPOINT, json={"query": user_text}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.Timeout:
        api_error = "timeout"
    except requests.ConnectionError:
        api_error = "connection"
    except requests.HTTPError as error:
        api_error = f"http_{error.response.status_code}"
    except requests.RequestException:
        api_error = "request_error"
    except ValueError:
        api_error = "invalid_json"

    # Fallback to local offline intent extraction
    roots = process_full_query(user_text)
    intent = get_best_intent(roots)
    return {
        "query": user_text,
        "answer_swahili": "Samahani, huduma ya taarifa rasmi haipatikani kwa sasa. Tafadhali wasiliana na ofisi husika ya chuo ili kupata maelezo sahihi.",
        "morphological_breakdown": {
            "tokens": user_text.split(),
            "extracted_roots": roots,
            "inferred_intent": intent
        },
        "grounding_source": None,
        "_api_error": api_error
    }


# ==========================================
# INTERFACE 1: MINIMALIST STUDENT EXPERIENCE
# ==========================================
if "Mwonekano wa mwanafunzi" in view_mode or "📱" in view_mode:
    st.title("Mshauri wa Kiswahili 🇰🇪")
    st.caption("Msaidizi wako rasmi wa sera na taaluma za chuo kikuu")

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    default_val = clean_selected_sample
    user_input = st.chat_input("Andika swali lako kwa Kiswahili...") or default_val

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Ninatafuta taarifa rasmi za chuo..."):
                res = query_backend(user_input)
                answer = res.get("answer_swahili", "")
                st.markdown(answer)

                doc = res.get("grounding_source")
                if doc:
                    with st.expander("📄 Chanzo cha taarifa"):
                        if doc.get("content_swahili"):
                            st.write(doc["content_swahili"])
                        elif doc.get("content_english"):
                            st.caption("Tafsiri ya Kiswahili haipo; maelezo yafuatayo yameandikwa kwa Kiingereza:")
                            st.write(doc["title"])
                            st.write(doc["content_english"])

        st.session_state.messages.append({"role": "assistant", "content": answer})


# ==========================================
# INTERFACE 2: HACKATHON PITCHING UI (JUDGES)
# ==========================================
else:
    st.title("Backend Deconstruction")
    st.caption("Live pipeline execution: Swahili Query -> Bantu Morphology -> Intent Classification -> GIN FTS -> Gemini Synthesis")

    col_input, col_pipe = st.columns([1, 1])

    with col_input:
        st.subheader("1. User Query & Local NLP Processing")
        test_q = st.text_area(
            "Input Kiswahili Query:",
            value=clean_selected_sample if clean_selected_sample else "Ninawezaje kulipa ada ya shule kwa awamu?",
            height=100
        )
        btn_run = st.button("Run Live Pipeline", use_container_width=True)

        if test_q or btn_run:
            local_roots = process_full_query(test_q)
            local_intent = get_best_intent(local_roots)

            st.markdown("<div class='card-box'>", unsafe_allow_html=True)
            st.markdown("#### NLP Morphology Engine")
            st.write(f"**Raw Tokens:** `{test_q.split()}`")
            st.write(f"**Stripped Extracted Roots:** `{local_roots}`")
            st.write(f"**Mapped SQL Search Intent:** `{local_intent}`")
            st.markdown("</div>", unsafe_allow_html=True)

    with col_pipe:
        st.subheader("2. Database Retrieval & Gemini Synthesis")
        if test_q or btn_run:
            api_res = query_backend(test_q)
            doc = api_res.get("grounding_source")
            inferred_intent = api_res.get("morphological_breakdown", {}).get("inferred_intent", local_intent)

            st.markdown("<div class='card-box'>", unsafe_allow_html=True)
            st.markdown("#### Database Retrieval & LLM Grounding")
            if api_error := api_res.get("_api_error"):
                st.error(f"Backend API error: {api_error}")
                st.write(f"**Nia iliyotambuliwa:** `{inferred_intent}`")
                st.caption("Hakikisha FastAPI inaendeshwa kwenye port 8000 (API_ENDPOINT).")
            elif doc:
                st.success(f"✅ Matched Document ID: #{doc.get('id')} — {doc.get('title')}")
                st.write(f"**English Knowledge Snippet:** _{doc.get('content_english')}_")
            else:
                st.warning("⚠️ **Fallback Response Triggered (Unmapped Intent / No Document Match)**")
                st.write(f"**Nia iliyotambuliwa:** `{inferred_intent}`")
                st.caption("Hakuna sera au hati inayolingana katika hifadhidata. Mfumo unatoa jibu la tahadhari ambalo halibuni tarehe, ada au sheria za uongo.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card-box'>", unsafe_allow_html=True)
            st.markdown("#### Final Output: AI Grounded Swahili response")
            st.markdown(api_res.get("answer_swahili", ""))
            st.markdown("</div>", unsafe_allow_html=True)
