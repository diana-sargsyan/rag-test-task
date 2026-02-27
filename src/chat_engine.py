"""Chat engine: manages conversation history, query rewriting, and agent orchestration."""

from openai import OpenAI

from src.agent import Agent
from src.data_manager import DataManager

REWRITE_PROMPT = """You are a query rewriter. Given a conversation history and the latest user message, rewrite the user message as a standalone question that can be understood without the conversation context.

Rules:
- If the message is already self-contained, return it unchanged.
- Resolve pronouns (they, their, it, them) and references (that client, those invoices) using conversation context.
- Keep the rewritten question concise and natural.
- Return ONLY the rewritten question, nothing else."""


class ChatEngine:
    """Orchestrates conversation flow with memory and query rewriting."""

    def __init__(self, model: str = "gpt-5.1", api_key: str | None = None):
        self.model = model
        self.api_key = api_key
        self.dm = DataManager()
        self.agent = Agent(self.dm, model=model, api_key=api_key)
        self.history: list[dict] = []
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()

    def set_model(self, model: str) -> None:
        """Switch the LLM model."""
        self.model = model
        self.agent = Agent(self.dm, model=model, api_key=self.api_key)

    def _rewrite_query(self, user_message: str) -> str:
        """Rewrite an ambiguous user message into a standalone question using conversation context."""
        if len(self.history) < 2:
            return user_message

        context_messages = [{"role": "system", "content": REWRITE_PROMPT}]
        # Include recent conversation for context (last 6 turns max)
        recent = self.history[-6:]
        for msg in recent:
            context_messages.append({"role": msg["role"], "content": msg["content"]})
        context_messages.append({"role": "user", "content": f"Rewrite this message: {user_message}"})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=context_messages,
                temperature=0,
                max_tokens=200,
            )
            rewritten = response.choices[0].message.content.strip()
            return rewritten if rewritten else user_message
        except Exception:
            return user_message

    def chat(self, user_message: str) -> dict:
        """Process a user message and return structured response.

        Returns: {answer, sql_queries, data_tables, rewritten_query}
        """
        rewritten = self._rewrite_query(user_message)

        # Build messages for the agent: conversation history + current query
        agent_messages = []
        for msg in self.history:
            agent_messages.append({"role": msg["role"], "content": msg["content"]})
        agent_messages.append({"role": "user", "content": rewritten})

        result = self.agent.run(agent_messages)

        # Update conversation history
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": result["answer"]})

        result["rewritten_query"] = rewritten if rewritten != user_message else None
        return result

    def reset(self) -> None:
        """Clear conversation history."""
        self.history.clear()
