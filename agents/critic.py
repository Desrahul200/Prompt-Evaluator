# agents/critic.py
from autogen import AssistantAgent


class CriticAgent(AssistantAgent):
    """
    Rates an ANSWER on Correctness, Hallucination, Tone, Relevance.
    """

    def __init__(
        self,
        llm_config,
        name: str = "CriticAgent",
        system_message: str | None = None,
        **kwargs,
    ):
        if system_message is None:
            system_message = (
                "You are an evaluator. For any ANSWER you receive, "
                "return exactly four lines:\n"
                "Correctness: Low/Medium/High – reason\n"
                "Hallucination: Low/Medium/High – reason\n"
                "Tone: Low/Medium/High – reason\n"
                "Relevance: Low/Medium/High – reason"
            )

        super().__init__(
            name=name,
            llm_config=llm_config,
            code_execution_config=False,     # no Docker
            system_message=system_message,
            **kwargs,
        )

    # ---- single-turn helper --------------------------------------------------
    def evaluate(self, answer: str) -> str:
        prompt = f"Evaluate the following.\nANSWER: {answer.strip()}"
        reply  = self.generate_reply([{"role": "user", "content": prompt}])
        return reply if isinstance(reply, str) else reply.get("content", "")
