import os
import requests
import streamlit as st
from morphology import process_full_query
from intent_map import get_best_intent

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000/api/v1/query/")

st.set_page_config(
    page_title="Mshauri Kiswahili 🇰🇪",
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
st.sidebar.title("Mshauri Kiswahili")
st.sidebar.caption("Bantu Computational Linguistics & Gemini 2.5 RAG")

view_mode = st.sidebar.radio(
    "Chagua Muonekano (Select View):",
    [
        "📱 Minimalist Student UI (Live User Experience)",
        "🔬 Hackathon Pitching UI (Backend Deconstruction for Judges)"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Sample Test Queries:**")
sample_queries = [
    "Ninawezaje kulipa ada ya shule kwa awamu?",
    "Nini kitatokea nisiposajili vitengo vyangu?",
    "Nimepoteza kitambulisho changu, nifanyeje?",
    "Ratiba ya mitihani itatoka lini?",
    "Ninawezaje kuomba mkopo wa HELB?"
]
selected_sample = st.sidebar.selectbox("Chagua Swali la Mfano:", ["-- Andika Yako --"] + sample_queries)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to Query Backend API
def query_backend(user_text: str):
    try:
        resp = requests.post(API_ENDPOINT, json={"query": user_text}, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    # Fallback to local offline intent extraction
    roots = process_full_query(user_text)
    intent = get_best_intent(roots)
    return {
        "query": user_text,
        "answer_swahili": f"Kulingana na mfumo wa Mshauri Kiswahili (Sera: `{intent}`):\n\nTafadhali hakikisha unazingatia sheria rasmi za chuo kikuu.",
        "morphological_breakdown": {
            "tokens": user_text.split(),
            "extracted_roots": roots,
            "inferred_intent": intent
        },
        "grounding_source": None
    }


# ==========================================
# INTERFACE 1: MINIMALIST STUDENT EXPERIENCE
# ==========================================
if "📱 Minimalist" in view_mode:
    st.title("Mshauri Kiswahili 🇰🇪")
    st.caption("Msaidizi wako rasmi wa sera na taaluma za chuo kikuu")

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    default_val = selected_sample if selected_sample != "-- Andika Yako --" else ""
    user_input = st.chat_input("Andika swali lako kwa Kiswahili...") or default_val

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Inachanganua sarufi na kutafuta sera..."):
                res = query_backend(user_input)
                answer = res.get("answer_swahili", "")
                st.markdown(answer)
                
                doc = res.get("grounding_source")
                if doc:
                    with st.expander("📄 Chanzo cha Sera (Official Policy Document)"):
                        st.caption(f"**{doc.get('title')}** (Category: `{doc.get('category')}`) ")
                        st.write(doc.get("content_english"))

        st.session_state.messages.append({"role": "assistant", "content": answer})


# ==========================================
# INTERFACE 2: HACKATHON PITCHING UI (JUDGES)
# ==========================================
else:
    st.title("🔬 Hackathon Pitching Interface — Backend Deconstruction")
    st.caption("Live pipeline execution: Swahili Query -> Bantu Morphology -> Intent Classification -> GIN FTS -> Gemini Synthesis")

    col_input, col_pipe = st.columns([1, 1])

    with col_input:
        st.subheader("1. User Query & Local NLP Processing")
        test_q = st.text_area(
            "Input Kiswahili Query:",
            value=selected_sample if selected_sample != "-- Andika Yako --" else "Ninawezaje kulipa ada ya shule kwa awamu?",
            height=100
        )
        btn_run = st.button("🚀 Run Live Pipeline", use_container_width=True)

        if test_q or btn_run:
            local_roots = process_full_query(test_q)
            local_intent = get_best_intent(local_roots)

            st.markdown("<div class='card-box'>", unsafe_allow_html=True)
            st.markdown("#### 🔹 Person B: NLP Morphology Engine")
            st.write(f"**Raw Tokens:** `{test_q.split()}`")
            st.write(f"**Stripped Extracted Roots:** `{local_roots}`")
            st.write(f"**Mapped SQL Search Intent:** `{local_intent}`")
            st.markdown("</div>", unsafe_allow_html=True)

    with col_pipe:
        st.subheader("2. Database Retrieval & Gemini Synthesis")
        if test_q or btn_run:
            api_res = query_backend(test_q)
            doc = api_res.get("grounding_source")

            st.markdown("<div class='card-box'>", unsafe_allow_html=True)
            st.markdown("#### 🔹 Person A: Database Retrieval & LLM")
            if doc:
                st.success(f"Matched Document ID: #{doc.get('id')} — {doc.get('title')}")
                st.write(f"**English Knowledge Snippet:** _{doc.get('content_english')}_")
            else:
                st.warning("No PostgreSQL GIN index match found. Using fallback intent.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card-box'>", unsafe_allow_html=True)
            st.markdown("#### 🔹 Final Output: Gemini 2.5 Grounded Swahili")
            st.markdown(api_res.get("answer_swahili", ""))
            st.markdown("</div>", unsafe_allow_html=True)