from autogen import AssistantAgent

class ComparatorAgent(AssistantAgent):
    def __init__(self, llm_config, name="ComparatorAgent",
                 system_message=None, **kwargs):
        if system_message is None:
            system_message = (
                "Given answer A and answer B, decide which is better …"
            )
        super().__init__(
            name=name,
            llm_config=llm_config,
            code_execution_config=False,
            system_message=system_message,
            **kwargs,
        )


    def compare(self, answer_a: str, answer_b: str) -> str:
        prompt = (
            "A:\n" + answer_a.strip() +
            "\n\nB:\n" + answer_b.strip()
        )
        reply = self.generate_reply([{"role": "user", "content": prompt}])
        return reply if isinstance(reply, str) else reply.get("content", "")
