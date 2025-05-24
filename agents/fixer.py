# agents/fixer.py  ─── stricter prompt-rewriter
from autogen import AssistantAgent
from typing import List
import re


class PromptFixerAgent(AssistantAgent):
    """
    Rewrites a PROMPT into two clearer bullet-line versions
    while preserving the original intent and keywords.
    """

    def __init__(
        self,
        llm_config,
        name: str = "PromptFixerAgent",
        system_message: str | None = None,
        **kwargs,
    ):
        if system_message is None:
            system_message = (
                "Rewrite the PROMPT you receive in **exactly two** clearer, more "
                "specific versions. Each version must:\n"
                "• Keep the same intent (do NOT ask a new or broader question).\n"
                "• Retain the main keyword(s) from the original (e.g. “Python”).\n"
                "• Avoid asking the user what they want—instead, assume they want a factual answer.\n"
                "Respond with **only two bullet lines** (start each with •). "
                "Return nothing else—no explanations, no code fences."
            )

        super().__init__(
            name=name,
            llm_config=llm_config,
            code_execution_config=False,
            system_message=system_message,
            **kwargs,
        )

    # ── public helper the app calls
    def fix(self, original_prompt: str) -> List[str]:
        ask = (
            f"PROMPT:\n{original_prompt.strip()}\n\n"
            "Rewrite per your instructions above."
        )
        reply = self.generate_reply([{"role": "user", "content": ask}])
        txt = reply if isinstance(reply, str) else reply.get("content", "")

        bullets = [
            ln.lstrip("•- ").strip()
            for ln in txt.splitlines()
            if ln.lstrip().startswith(("•", "-"))
        ]

        # simple guard: keep only bullets that still mention at least
        # one word from original prompt (case-insensitive, ≥4 letters)
        keywords = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", original_prompt)]
        filtered = [
            b for b in bullets
            if any(k in b.lower() for k in keywords)
        ]

        return filtered[:2]  # may return [] if model misbehaves
