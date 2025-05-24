import os
from agents import CriticAgent, PromptFixerAgent, ComparatorAgent
from autogen import AssistantAgent

os.environ["AUTOGEN_USE_DOCKER"] = "0"
LLM = {
    "temperature": 0.7,
    "config_list": [{
        "model": "llama3-70b-8192",
        "api_key": os.getenv("GROQ_API_KEY"),
        "base_url": "https://api.groq.com/openai/v1",
        "price": [0.0, 0.0],
    }]
}

critic = CriticAgent(LLM)
fixer  = PromptFixerAgent(LLM)
gen    = AssistantAgent("Generator", llm_config=LLM, code_execution_config=False)
comp   = ComparatorAgent(LLM)

PROMPT   = "What is Python?"
ANSWER_A = "Python is a programming language."

print("\n=== Critic ===")
print(critic.evaluate(ANSWER_A))

print("\n=== Fixer ===")
improved = fixer.fix(PROMPT)
print(improved)

print("\n=== Generator (B) ===")
answer_b = gen.generate_reply([{"role": "user", "content": improved[0]}])
answer_b = answer_b if isinstance(answer_b, str) else answer_b.get("content", "")
print(answer_b)

print("\n=== Comparator ===")
print(comp.compare(ANSWER_A, answer_b))
