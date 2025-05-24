# app.py ────────────────────────────────────────────────────────────────────
import streamlit as st
import json
from main import PromptEvaluator
from config import SUPPORTED_MODELS, update_config_for_model

# ── Basic page setup ───────────────────────────────────────────────────────
st.set_page_config("AutoGen Prompt Evaluator", layout="wide")

# custom CSS: orange accents, grey background cards
st.markdown(
    """
    <style>
    :root      { --orange: #f57c00; --greybg: #f7f7f7; }
    .stButton>button           { background-color: var(--orange); border: none;}
    .stButton>button:hover     { background-color: #ffa040; }
    .stDownloadButton>button   { background-color: var(--orange); }
    div[data-testid="stVerticalBlock"]>div>div:has(.stTabs) { background: var(--greybg); padding: 0.5rem 1rem 1rem;}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"]
        { color: var(--orange); border-color: var(--orange);}
    </style>
    """,
    unsafe_allow_html=True,
)

# helper for cross-version rerun
def _rerun():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# ── initialise evaluator in session ────────────────────────────────────────
if "evaluator" not in st.session_state:
    st.session_state.evaluator = PromptEvaluator()
st.session_state.setdefault("first_pass", None)
st.session_state.setdefault("final_pass", None)

# ── sidebar ────────────────────────────────────────────────────────────────
model_choice = st.sidebar.selectbox("LLM backend", SUPPORTED_MODELS)

if st.session_state.get("last_model") != model_choice:
    st.session_state.last_model = model_choice
    st.session_state.evaluator.update_llm_config(
        update_config_for_model(model_choice)
    )
    st.sidebar.success(f"Switched to {model_choice}")

if st.sidebar.button("Clear session"):
    st.session_state.first_pass = None
    st.session_state.final_pass = None
    _rerun()

# ── header & input ─────────────────────────────────────────────────────────
st.title("AutoGen Prompt Evaluator")

st.markdown(
    """
| Agent                | Role                                                                 |
|----------------------|----------------------------------------------------------------------|
| **CriticAgent**      | Rates correctness, hallucination risk, tone, relevance               |
| **PromptFixerAgent** | Rewrites your prompt in two clearer versions                         |
| **GeneratorAgent**   | Produces a new answer (B) from the first improved prompt             |
| **ComparatorAgent**  | Decides whether answer A or answer B is better                       |
"""
)

c1, c2 = st.columns(2)
with c1:
    prompt_text = st.text_area("Prompt", height=160)
with c2:
    answer_a_text = st.text_area("Answer A (existing LLM output)", height=160)

# ── run button ─────────────────────────────────────────────────────────────
if st.button("Run Evaluation", use_container_width=True):
    if not prompt_text.strip() or not answer_a_text.strip():
        st.error("Please fill in both the prompt and Answer A.")
        st.stop()

    with st.spinner("Running full evaluation …"):
        res = st.session_state.evaluator.evaluate_prompt_response(
            prompt_text, answer_a_text, chosen_prompt=None  # first bullet
        )
    st.session_state.final_pass = res  # save for download

    # display results
    tab_critic, tab_fixer, tab_comp = st.tabs(
        ["Critic Analysis", "Improved Prompts", "Response Comparison"]
    )

    with tab_critic:
        st.subheader("Critic Analysis")
        st.code(res["critic_analysis"], language="markdown")

    with tab_fixer:
        st.subheader("Improved Prompts (first one was used)")
        for i, txt in enumerate(res["improved_prompts"], 1):
            st.markdown(f"**Version {i}**")
            st.code(txt, language="markdown")

    with tab_comp:
        st.subheader("Comparator Verdict")
        st.code(res["comparison_analysis"], language="markdown")

        st.markdown("**Answer A**")
        st.code(res["original_response"], language="markdown")

        st.markdown("**Prompt used for Answer B**")
        st.code(res["chosen_prompt"], language="markdown")

        st.markdown("**Answer B**")
        st.code(res["new_response"], language="markdown")

    # optional JSON
    if st.sidebar.toggle("Export results as JSON", key="dl", value=False):
        st.sidebar.download_button(
            "Download results.json",
            data=json.dumps(res, indent=2),
            file_name="evaluation_results.json",
            mime="application/json",
            use_container_width=True,
        )
