import json
import logging
import uuid
from typing import Any

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from context_memory import MemoryService, _user_entity_ids

logger = logging.getLogger(__name__)


def _message_content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "".join(parts).strip()
    return str(content)


class ContextGraphAgent:
    """Agent backed by neo4j-agent-memory with per-user context isolation."""

    def __init__(
        self,
        memory_service: MemoryService,
        llm_api_key: str,
        *,
        user_id: str,
        session_id: str | None = None,
        model: str = "gemini-3.5-flash",
    ):
        self.memory = memory_service
        self.user_id = user_id
        self.session_id = session_id or str(uuid.uuid4())
        self.llm = ChatGoogleGenerativeAI(api_key=llm_api_key, model=model)
        self.tools = self._setup_tools()
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=(
                "You are a healthcare context graph assistant powered by Neo4j Agent Memory. "
                "Each clinician or workspace has a private context graph — only use memory tools "
                "for this user's data. You have conversation history, extracted entities, "
                "preferences, and reasoning traces scoped to the current user. "
                "Always use memory tools before answering."
            ),
        )

    def _setup_tools(self) -> list:
        memory = self.memory
        session_id = self.session_id
        user_id = self.user_id

        @tool
        def memory_search(query: str) -> str:
            """Search this user's context graph memory: messages, entities, preferences, traces."""
            try:
                results = memory.search(query, user_id=user_id, session_id=session_id)
                return json.dumps(results, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)}, default=str)

        @tool
        def memory_get_context(query: str) -> str:
            """Get assembled context from this user's short-term, long-term, and reasoning memory."""
            try:
                result = memory.get_context(query, user_id=user_id, session_id=session_id)
                return json.dumps(result, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)}, default=str)

        @tool
        def memory_search_entities(query: str) -> str:
            """Search extracted entities in this user's long-term memory."""

            async def _search() -> list[dict[str, Any]]:
                client = memory.integration.client
                allowed_ids = await _user_entity_ids(client, user_id)
                entities = await client.long_term.search_entities(query, limit=20)
                return [
                    {
                        "name": e.display_name,
                        "type": str(e.type),
                        "description": e.description,
                    }
                    for e in entities
                    if str(e.id) in allowed_ids
                ][:15]

            try:
                rows = memory.run(_search())
                return json.dumps(rows, default=str)
            except Exception as e:
                return json.dumps({"error": str(e)}, default=str)

        return [memory_search, memory_get_context, memory_search_entities]

    def query(self, user_input: str) -> str:
        try:
            return self.memory.run(self._aquery(user_input))
        except Exception as e:
            logger.error(f"Agent error: {e}")
            return f"Error processing request: {str(e)}"

    async def _aquery(self, user_input: str) -> str:
        client = self.memory.integration.client
        session_id = self.session_id
        user_id = self.user_id

        self.memory.store_message("user", user_input, user_id=user_id, session_id=session_id)

        trace = await client.reasoning.start_trace(
            session_id,
            user_input,
            user_identifier=user_id,
        )

        try:
            ctx = self.memory.get_context(
                user_input, user_id=user_id, session_id=session_id
            )
            context_text = ctx.get("context", "") if isinstance(ctx, dict) else str(ctx)

            prompt = (
                f"Context graph memory for user `{user_id}`:\n{context_text}\n\n"
                f"User question: {user_input}"
            )

            result = self.agent.invoke({"messages": [{"role": "user", "content": prompt}]})
            response = _message_content_to_text(result["messages"][-1].content)

            self.memory.store_message(
                "assistant", response, user_id=user_id, session_id=session_id
            )

            await client.reasoning.complete_trace(
                trace.id,
                outcome=response,
                success=True,
            )
            return response
        except Exception as exc:
            await client.reasoning.complete_trace(
                trace.id,
                outcome=str(exc),
                success=False,
            )
            raise

    def reset_memory(self) -> str:
        old = self.session_id
        self.memory.clear_session(self.user_id, old)
        self.session_id = str(uuid.uuid4())
        return self.session_id
