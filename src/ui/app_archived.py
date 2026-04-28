# app.py

import streamlit as st
import requests
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="HR Policy Assistant",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1e1e2e;
    }
    [data-testid="stSidebar"] * {
        color: #cdd6f4 !important;
    }

    /* Chat bubbles */
    .user-bubble {
        background: #313244;
        border-radius: 12px 12px 2px 12px;
        padding: 12px 16px;
        margin: 6px 0 6px 60px;
        color: #cdd6f4;
        font-size: 0.95rem;
    }
    .assistant-bubble {
        background: #1e1e2e;
        border: 1px solid #313244;
        border-radius: 12px 12px 12px 2px;
        padding: 12px 16px;
        margin: 6px 60px 6px 0;
        color: #cdd6f4;
        font-size: 0.95rem;
    }
    .citation-box {
        background: #181825;
        border-left: 3px solid #89b4fa;
        border-radius: 0 6px 6px 0;
        padding: 8px 12px;
        margin-top: 8px;
        font-size: 0.82rem;
        color: #89dceb;
        font-family: monospace;
        white-space: pre-wrap;
    }
    .status-ok  { color: #a6e3a1; font-weight: 600; }
    .status-err { color: #f38ba8; font-weight: 600; }

    /* Hide default Streamlit chrome */
    #MainMenu, footer { visibility: hidden; }

    /* Input bar */
    .stTextInput > div > div > input {
        background: #313244;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []   # [{role, content, citations}]

if "api_ok" not in st.session_state:
    st.session_state.api_ok = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def check_health() -> bool:
    try:
        r = requests.get(f"{API_BASE}/health", timeout=4)
        return r.status_code == 200
    except Exception:
        return False


def send_query(question: str) -> dict:
    r = requests.post(f"{API_BASE}/query", params={"q": question}, timeout=60)
    r.raise_for_status()
    return r.json()


def ingest_files(files) -> dict:
    file_tuples = [("files", (f.name, f.getvalue(), "application/octet-stream")) for f in files]
    r = requests.post(f"{API_BASE}/ingest", files=file_tuples, timeout=120)
    r.raise_for_status()
    return r.json()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📋 HR Policy Assistant")
    st.markdown("---")

    # API health
    if st.button("🔌 Check API Status", use_container_width=True):
        st.session_state.api_ok = check_health()

    if st.session_state.api_ok is True:
        st.markdown('<p class="status-ok">● API Online</p>', unsafe_allow_html=True)
    elif st.session_state.api_ok is False:
        st.markdown('<p class="status-err">● API Offline</p>', unsafe_allow_html=True)
        st.caption(f"Expected at {API_BASE}")
    else:
        st.caption("Click above to check API status")

    st.markdown("---")

    # Document upload
    st.markdown("### 📁 Upload Documents")
    uploaded = st.file_uploader(
        "Drop .docx files here",
        type=["docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded:
        st.caption(f"{len(uploaded)} file(s) selected")
        if st.button("⬆️ Ingest Documents", use_container_width=True, type="primary"):
            with st.spinner("Ingesting…"):
                try:
                    result = ingest_files(uploaded)
                    logs = result.get("logs", [])
                    for log in logs:
                        icon = "✅" if log["status"] == "indexed" else "⏭️"
                        chunks = f"  ({log['chunks']} chunks)" if log["status"] == "indexed" else ""
                        st.markdown(f"{icon} **{log['filename']}** — {log['status']}{chunks}")
                except Exception as e:
                    st.error(f"Ingestion failed: {e}")

    st.markdown("---")

    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("Powered by GPT-4o-mini + HybridSearch")
    st.caption(f"Backend: `{API_BASE}`")


# ── Main: Chat ────────────────────────────────────────────────────────────────

st.markdown("## 💬 Ask a Policy Question")

# Render history
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align:center; padding: 60px 0; color: #6c7086;">
            <div style="font-size: 2.5rem">📋</div>
            <div style="margin-top: 12px; font-size: 1rem">
                Ask anything about HR policies, AML rules, onboarding procedures, or compensation.
            </div>
            <div style="margin-top: 6px; font-size: 0.85rem">
                Examples: <em>"What is the PTO carryover limit?"</em> &nbsp;|&nbsp;
                <em>"Who do I report suspicious activity to?"</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-bubble">🧑‍💼 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-bubble">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("citations"):
                st.markdown(f'<div class="citation-box">📎 Sources\n{msg["citations"]}</div>', unsafe_allow_html=True)


# ── Input bar ─────────────────────────────────────────────────────────────────

st.markdown("---")
col1, col2 = st.columns([9, 1])

with col1:
    question = st.text_input(
        "question",
        placeholder="e.g. What is the PTO carryover policy?",
        label_visibility="collapsed",
        key="question_input",
    )
with col2:
    send = st.button("Send ➤", type="primary", use_container_width=True)

# Suggested prompts
with st.expander("💡 Suggested questions", expanded=False):
    suggestions = [
        "What is the maximum PTO carryover allowed?",
        "Who must I report suspicious activity to?",
        "What documents are needed for High-Risk customer onboarding?",
        "What is the 401(k) vesting schedule?",
        "What steps should I take immediately after a data breach?",
        "What are the FMLA eligibility criteria?",
    ]
    cols = st.columns(3)
    for i, s in enumerate(suggestions):
        if cols[i % 3].button(s, key=f"sug_{i}", use_container_width=True):
            question = s
            send = True


# ── Handle send ───────────────────────────────────────────────────────────────

if send and question.strip():
    st.session_state.messages.append({"role": "user", "content": question.strip()})

    with st.spinner("Thinking…"):
        try:
            data = send_query(question.strip())
            answer   = data.get("answer", "No answer returned.")
            citations = data.get("citations", "")
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "citations": citations,
            })
        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "⚠️ Could not reach the API. Make sure the FastAPI server is running.",
                "citations": "",
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ Error: {e}",
                "citations": "",
            })

    st.rerun()