# multi_agent_prompt_evaluator.py
# Full prompt-debug pipeline with FOUR agents, no Docker.

import os, sys, autogen

# ── 0. Environment & model ───────────────────────────────────────────────────
os.environ["AUTOGEN_USE_DOCKER"] = "0"        # global: never try Docker

GROQ_KEY = os.getenv("GROQ_API_KEY") or "YOUR_GROQ_KEY_HERE"
if GROQ_KEY.startswith("YOUR_") or not GROQ_KEY.strip():
    sys.exit("⛔  Set GROQ_API_KEY env-var or replace YOUR_GROQ_KEY_HERE.")

MODEL_ID = "llama3-70b-8192"      # your account may also support mixtral
# MODEL_ID = "mixtral-8x7b-32768" # ← use this if llama3 unavailable

LLM = {
    "temperature": 0.7,
    "timeout": 600,
    "config_list": [{
        "model": MODEL_ID,
        "api_key": GROQ_KEY,
        "base_url": "https://api.groq.com/openai/v1",
        "price": [0.0, 0.0]        # silences “price” warnings
    }]
}

# ── 1. Define agents ─────────────────────────────────────────────────────────
CriticAgent = autogen.AssistantAgent(
    "Critic",
    llm_config=LLM,
    code_execution_config=False,
    system_message=(
        "You are an evaluator. For any ANSWER you receive, return exactly four "
        "lines labelled Correctness, Hallucination, Tone, Relevance "
        "(each Low/Medium/High – reason)."
    )
)

FixerAgent = autogen.AssistantAgent(
    "Fixer",
    llm_config=LLM,
    code_execution_config=False,
    system_message=(
        "Rewrite any PROMPT you receive in two clearer versions. "
        "Return exactly two bullet lines and nothing else."
    )
)

GeneratorAgent = autogen.AssistantAgent(
    "Generator",
    llm_config=LLM,
    code_execution_config=False,
    system_message="Answer prompts clearly, concisely, and accurately."
)

ComparatorAgent = autogen.AssistantAgent(
    "Comparator",
    llm_config=LLM,
    code_execution_config=False,
    system_message=(
        "Given answer A and answer B, decide which is better and explain why "
        "in one short paragraph."
    )
)

# ── 2. Helper to call any agent once ─────────────────────────────────────────
def single_turn(agent: autogen.AssistantAgent, prompt: str) -> str:
    history = [{"role": "user", "content": prompt}]
    reply   = agent.generate_reply(history)
    return (reply if isinstance(reply, str) else reply.get("content", "")).strip()

# ── 3. Demo data ─────────────────────────────────────────────────────────────
PROMPT   = "What is Python?"
ANSWER_A = "Python is a programming language."

# ── 4. Pipeline steps ────────────────────────────────────────────────────────

# ❶ Critic original answer
crit_prompt = (
    "Evaluate the following ANSWER.\nANSWER: " + ANSWER_A
)
print("\n===== Critic =====")
print(single_turn(CriticAgent, crit_prompt))

# ❷ Fixer improves the prompt
fix_prompt = (
    "Rewrite the PROMPT below in two clearer ways; return two bullet lines.\n\n"
    "PROMPT: " + PROMPT
)
fix_reply = single_turn(FixerAgent, fix_prompt)
print("\n===== Fixer =====")
print(fix_reply)

bullets = [
    ln.lstrip("•- ").strip() for ln in fix_reply.splitlines()
    if ln.lstrip().startswith(("•", "-"))
]
if len(bullets) < 2:
    sys.exit("⛔  Fixer did not return two bullet lines. "
             "Try a different model if this happens.")

IMPROVED_PROMPT = bullets[0]

# ❸ Generator creates new answer B
print("\n===== Generator (answer B) =====")
ANSWER_B = single_turn(GeneratorAgent, IMPROVED_PROMPT)
print(ANSWER_B)

# ❹ Comparator decides A vs B
compare_prompt = (
    "Which answer is better (A or B) and why?\n\nA:\n"
    f"{ANSWER_A}\n\nB:\n{ANSWER_B}"
)
print("\n===== Comparator verdict =====")
print(single_turn(ComparatorAgent, compare_prompt))
