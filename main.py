"""
main.py – orchestrates Critic → Fixer → Generator → Comparator
Uses the first improved prompt automatically.
"""
from typing import Dict, Any, Optional
from autogen import AssistantAgent
from agents import CriticAgent, PromptFixerAgent, ComparatorAgent
from config import get_llm_config


class PromptEvaluator:
    def __init__(self) -> None:
        # shared LLM config from config.py
        self.llm_config = get_llm_config()

        self.critic = CriticAgent(llm_config=self.llm_config)
        self.fixer = PromptFixerAgent(llm_config=self.llm_config)
        self.comp = ComparatorAgent(llm_config=self.llm_config)

        # neutral generator (no special evaluation role)
        self.generator = AssistantAgent(
            "GeneratorAgent",
            llm_config=self.llm_config,
            code_execution_config=False,
            system_message="Answer user prompts clearly, concisely, and accurately.",
        )

    # ────────────────────────────────────────────────────────────────── #
    def evaluate_prompt_response(
        self,
        prompt: str,
        answer_a: str,
        chosen_prompt: Optional[str] = None,   # optional override
    ) -> Dict[str, Any]:
        """
        Full pipeline:
        1. Critic evaluates Answer A
        2. Fixer rewrites prompt
        3. Pick first bullet (or chosen_prompt override)
        4. Generator produces Answer B
        5. Comparator judges A vs B
        Returns a dictionary for display / JSON export.
        """

        # 1️⃣ Critic
        critic_text = self.critic.evaluate(answer_a).strip()

        # 2️⃣ Fixer
        improved = self.fixer.fix(prompt)          # list[str]

        # choose prompt for Answer B
        if chosen_prompt and chosen_prompt in improved:
            use_prompt = chosen_prompt
        else:
            use_prompt = (improved or [prompt])[0]   # first bullet or original

        # 3️⃣ Generator → Answer B
        raw = self.generator.generate_reply(
            [{"role": "user", "content": use_prompt}]
        )
        answer_b = raw if isinstance(raw, str) else raw.get("content", "")
        answer_b = (answer_b or "").strip()

        # 4️⃣ Comparator
        comp_text = (
            self.comp.compare(answer_a, answer_b).strip()
            if len(answer_b) > 10
            else "Comparison skipped – new answer not meaningful."
        )

        # 5️⃣ pack results
        return {
            "original_prompt": prompt,
            "original_response": answer_a,
            "critic_analysis": critic_text,
            "improved_prompts": improved,
            "chosen_prompt": use_prompt,
            "new_response": answer_b,
            "comparison_analysis": comp_text,
        }

    # allow sidebar model switching
    def update_llm_config(self, cfg: Dict[str, Any]) -> None:
        self.llm_config = cfg
        for agent in (self.critic, self.fixer, self.comp, self.generator):
            agent.llm_config = cfg
