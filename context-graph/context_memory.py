"""Neo4j Agent Memory service wrapper for Streamlit (per-user context graphs)."""

from __future__ import annotations

import asyncio
import logging
import os
import threading
from typing import Any

from pydantic import SecretStr

from neo4j_agent_memory import MemoryIntegration, MemorySettings
from neo4j_agent_memory.config.settings import MemoryConfig, Neo4jConfig

logger = logging.getLogger(__name__)

HEALTHCARE_BOOTSTRAP = [
    (
        "user",
        "Patient Maria Gonzalez, age 58, has Type 2 diabetes and essential hypertension. "
        "She takes Metformin 500mg and Lisinopril 10mg. Dr. Amanda Foster at Riverside General "
        "Hospital manages her care. Recent HbA1c was 8.2%.",
    ),
    (
        "user",
        "Patient James Wilson, age 72, has congestive heart failure (NYHA Class II). "
        "Dr. Michael Torres is his cardiologist at Riverside General. He is on Furosemide 40mg. "
        "BNP was 980 pg/mL on admission.",
    ),
    (
        "user",
        "Patient Sarah Chen, age 34, was diagnosed with postpartum depression after delivery. "
        "Dr. Lisa Nguyen at Northside Women's Health Center started Sertraline 50mg.",
    ),
    (
        "user",
        "Patient Robert Kim, age 45, has persistent asthma. Dr. Amanda Foster prescribed "
        "an Albuterol rescue inhaler. Peak flow was 320 L/min.",
    ),
    (
        "user",
        "Patient Elena Patel, age 67, had osteoarthritis of the hip and underwent total hip "
        "arthroplasty at Riverside General. Dr. David Brooks performed surgery and ordered "
        "a 12-week physical therapy program.",
    ),
]

USER_ENTITY_IDS = """
MATCH (u:User {identifier: $user_id})-[:HAS_CONVERSATION]->(:Conversation)
      -[:HAS_MESSAGE]->(:Message)<-[:EXTRACTED_FROM]-(e:Entity)
RETURN DISTINCT e.id AS id
"""

USER_STATS = """
MATCH (u:User {identifier: $user_id})
OPTIONAL MATCH (u)-[:HAS_CONVERSATION]->(c:Conversation)
OPTIONAL MATCH (c)-[:HAS_MESSAGE]->(m:Message)
WITH u, count(DISTINCT c) AS conversations, count(DISTINCT m) AS messages
OPTIONAL MATCH (u)-[:HAS_TRACE]->(rt:ReasoningTrace)
WITH conversations, messages, count(DISTINCT rt) AS reasoning_traces
OPTIONAL MATCH (u)-[:HAS_CONVERSATION]->(:Conversation)-[:HAS_MESSAGE]->(:Message)
      <-[:EXTRACTED_FROM]-(e:Entity)
RETURN conversations, messages, reasoning_traces, count(DISTINCT e) AS entities
"""

USER_GRAPH = """
MATCH (u:User {identifier: $user_id})
OPTIONAL MATCH (u)-[:HAS_CONVERSATION]->(c:Conversation)
OPTIONAL MATCH (c)-[hm:HAS_MESSAGE]->(m:Message)
OPTIONAL MATCH (e:Entity)-[ef:EXTRACTED_FROM]->(m)
OPTIONAL MATCH (e)-[er:RELATED_TO]-(e2:Entity)
WHERE EXISTS {
    MATCH (u)-[:HAS_CONVERSATION]->(:Conversation)-[:HAS_MESSAGE]->(:Message)
          <-[:EXTRACTED_FROM]-(e2)
}
OPTIONAL MATCH (u)-[:HAS_TRACE]->(rt:ReasoningTrace)
WHERE ($session_id IS NULL OR c.session_id = $session_id OR rt.session_id = $session_id)
RETURN u, c, hm, m, e, ef, er, e2, rt
LIMIT $limit
"""


def build_memory_settings() -> MemorySettings:
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    llm = os.getenv("MEMORY_LLM", f"gemini/{model}")
    embedding = os.getenv(
        "MEMORY_EMBEDDING",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    multi_tenant = os.getenv("MEMORY_MULTI_TENANT", "true").lower() == "true"

    return MemorySettings(
        neo4j=Neo4jConfig(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USER", "neo4j"),
            password=SecretStr(os.getenv("NEO4J_PASSWORD", "password")),
            database=os.getenv("NEO4J_DATABASE", "neo4j"),
        ),
        llm=llm,
        embedding=embedding,
        memory=MemoryConfig(multi_tenant=multi_tenant),
    )


class MemoryService:
    """Sync facade over MemoryIntegration for Streamlit, scoped per user."""

    def __init__(self) -> None:
        self._integration: MemoryIntegration | None = None
        self._connected = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._ready = threading.Event()

    @property
    def integration(self) -> MemoryIntegration:
        if not self._integration or not self._connected:
            raise RuntimeError("MemoryService not connected")
        return self._integration

    def _start_loop_thread(self) -> None:
        if self._loop is not None:
            return

        def _run() -> None:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._ready.set()
            self._loop.run_forever()

        self._thread = threading.Thread(target=_run, name="memory-service-loop", daemon=True)
        self._thread.start()
        self._ready.wait()

    def run(self, coro: Any, timeout: float = 300) -> Any:
        """Run async code on the dedicated memory thread (Streamlit-safe)."""
        self._start_loop_thread()
        assert self._loop is not None
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    def connect(self) -> None:
        if self._connected:
            return

        self._start_loop_thread()

        async def _connect() -> MemoryIntegration:
            from neo4j_agent_memory import MemoryClient

            settings = build_memory_settings()
            client = MemoryClient(settings)
            await client.connect()
            return MemoryIntegration(
                client=client,
                session_strategy="per_conversation",
                auto_extract=os.getenv("MEMORY_AUTO_EXTRACT", "true").lower() == "true",
                auto_preferences=False,
            )

        self._integration = self.run(_connect())
        self._connected = True
        logger.info("Connected neo4j-agent-memory (per-user context graph)")

    def ensure_user(self, user_id: str) -> None:
        ensure_user_registered(self, user_id)

    def get_session_id(self, hint: str | None = None) -> str:
        return self.integration.resolve_session_id(hint)

    def store_message(
        self,
        role: str,
        content: str,
        *,
        user_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        self.ensure_user(user_id)
        client = self.integration.client

        async def _store() -> dict[str, Any]:
            message = await client.short_term.add_message(
                session_id=session_id,
                role=role,
                content=content,
                user_identifier=user_id,
                extract_entities=self.integration._auto_extract,
                generate_embedding=True,
            )
            return {
                "stored": True,
                "type": "message",
                "id": str(message.id),
                "session_id": session_id,
                "user_id": user_id,
            }

        return self.run(_store())

    def get_context(
        self,
        query: str,
        *,
        user_id: str,
        session_id: str,
    ) -> dict[str, Any]:
        self.ensure_user(user_id)
        client = self.integration.client
        max_items = int(os.getenv("MEMORY_CONTEXT_ITEMS", "12"))

        async def _context() -> dict[str, Any]:
            parts: list[str] = []

            conv = await client.short_term.get_conversation(session_id, limit=max_items)
            if conv and conv.messages:
                parts.append("## Conversation History")
                for msg in conv.messages[-max_items:]:
                    role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
                    parts.append(f"**{role}**: {msg.content}")

            prefs = await client.long_term.get_preferences_for(user_id)
            if prefs:
                parts.append("\n## User Preferences")
                for pref in prefs[:max_items]:
                    line = f"- [{pref.category}] {pref.preference}"
                    if pref.context:
                        line += f" (context: {pref.context})"
                    parts.append(line)

            allowed_ids = await _user_entity_ids(client, user_id)
            entities = await client.long_term.search_entities(query, limit=max_items * 2)
            user_entities = [e for e in entities if str(e.id) in allowed_ids][:max_items]
            if user_entities:
                parts.append("\n## Relevant Knowledge")
                for entity in user_entities:
                    line = f"- {entity.display_name} ({entity.full_type})"
                    if entity.description:
                        line += f": {entity.description}"
                    parts.append(line)

            traces = await _user_similar_traces(client, user_id, query, limit=max_items // 2)
            if traces:
                parts.append("\n## Similar Past Tasks")
                for trace in traces:
                    parts.append(f"- {trace['task']}: {trace.get('outcome', '')}")

            context = "\n".join(parts)
            return {
                "session_id": session_id,
                "user_id": user_id,
                "context": context,
                "has_context": bool(context),
            }

        return self.run(_context())

    def search(
        self,
        query: str,
        *,
        user_id: str,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        self.ensure_user(user_id)
        client = self.integration.client

        async def _search() -> dict[str, Any]:
            results: dict[str, list[dict[str, Any]]] = {"messages": [], "entities": [], "preferences": []}

            messages = await client.short_term.search_messages(
                query=query,
                session_id=session_id,
                limit=10,
            )
            results["messages"] = [
                {
                    "id": str(msg.id),
                    "role": msg.role.value if hasattr(msg.role, "value") else str(msg.role),
                    "content": msg.content,
                }
                for msg in messages
            ]

            allowed_ids = await _user_entity_ids(client, user_id)
            entities = await client.long_term.search_entities(query, limit=20)
            results["entities"] = [
                {
                    "id": str(entity.id),
                    "name": entity.display_name,
                    "type": (
                        entity.type.value
                        if hasattr(entity.type, "value")
                        else str(entity.type)
                    ),
                    "description": entity.description,
                }
                for entity in entities
                if str(entity.id) in allowed_ids
            ][:10]

            prefs = await client.long_term.get_preferences_for(user_id)
            query_lower = query.lower()
            results["preferences"] = [
                {
                    "id": str(pref.id),
                    "category": pref.category,
                    "preference": pref.preference,
                    "context": pref.context,
                }
                for pref in prefs
                if query_lower in pref.preference.lower()
                or query_lower in (pref.context or "").lower()
            ]

            results["traces"] = await _user_similar_traces(client, user_id, query, limit=5)
            return {"results": results, "query": query, "user_id": user_id}

        return self.run(_search())

    def get_stats(self, *, user_id: str, session_id: str | None = None) -> dict[str, Any]:
        self.ensure_user(user_id)
        client = self.integration.client

        async def _stats() -> dict[str, Any]:
            rows = await client.query.cypher(USER_STATS, {"user_id": user_id})
            row = rows[0] if rows else {}
            session_msgs = 0
            if session_id:
                conv = await client.short_term.get_conversation(session_id, limit=500)
                session_msgs = len(conv.messages) if conv else 0
            return {
                "user_id": user_id,
                "entities": row.get("entities", 0),
                "messages": row.get("messages", 0),
                "reasoning_traces": row.get("reasoning_traces", 0),
                "conversations": row.get("conversations", 0),
                "messages_in_session": session_msgs,
            }

        return self.run(_stats())

    def export_graph(self, *, user_id: str, session_id: str | None = None) -> dict[str, Any]:
        self.ensure_user(user_id)
        client = self.integration.client

        async def _export() -> dict[str, Any]:
            rows = await client.query.cypher(
                USER_GRAPH,
                {"user_id": user_id, "session_id": session_id, "limit": 500},
            )
            nodes: list[dict[str, Any]] = []
            relationships: list[dict[str, Any]] = []
            seen_nodes: set[str] = set()
            seen_rels: set[str] = set()

            def add_node(raw: dict[str, Any] | None, labels: list[str]) -> str | None:
                if not raw:
                    return None
                node_id = raw.get("id")
                if not node_id or node_id in seen_nodes:
                    return node_id
                props = {k: v for k, v in raw.items() if v is not None and k != "embedding"}
                nodes.append({"id": node_id, "labels": labels, "properties": props})
                seen_nodes.add(node_id)
                return node_id

            def add_rel(rel_type: str, from_id: str | None, to_id: str | None) -> None:
                if not from_id or not to_id:
                    return
                rel_id = f"{from_id}->{rel_type}->{to_id}"
                if rel_id in seen_rels:
                    return
                relationships.append(
                    {"id": rel_id, "type": rel_type, "from_node": from_id, "to_node": to_id}
                )
                seen_rels.add(rel_id)

            for row in rows:
                user_node = add_node(dict(row["u"]) if row.get("u") else None, ["User"])
                conv_node = add_node(dict(row["c"]) if row.get("c") else None, ["Conversation"])
                msg_node = add_node(dict(row["m"]) if row.get("m") else None, ["Message"])
                entity_node = add_node(dict(row["e"]) if row.get("e") else None, ["Entity"])
                entity2_node = add_node(dict(row["e2"]) if row.get("e2") else None, ["Entity"])
                trace_node = add_node(dict(row["rt"]) if row.get("rt") else None, ["ReasoningTrace"])

                if user_node and conv_node:
                    add_rel("HAS_CONVERSATION", user_node, conv_node)
                if conv_node and msg_node:
                    add_rel("HAS_MESSAGE", conv_node, msg_node)
                if entity_node and msg_node:
                    add_rel("EXTRACTED_FROM", entity_node, msg_node)
                if entity_node and entity2_node and row.get("er"):
                    add_rel("RELATED_TO", entity_node, entity2_node)
                if user_node and trace_node:
                    add_rel("HAS_TRACE", user_node, trace_node)

            return {"nodes": nodes, "relationships": relationships, "user_id": user_id}

        return self.run(_export())

    def bootstrap_healthcare(self, *, user_id: str, session_id: str | None = None) -> int:
        """Seed clinical narratives for a single user's context graph."""
        sid = session_id or f"{user_id}-healthcare-bootstrap"
        count = 0
        for role, content in HEALTHCARE_BOOTSTRAP:
            self.store_message(role, content, user_id=user_id, session_id=sid)
            count += 1
        return count

    def clear_session(self, user_id: str, session_id: str) -> None:
        self.run(self.integration.client.short_term.clear_session(session_id))


def ensure_user_registered(service: MemoryService, user_id: str) -> None:
    """Register or update a :User node (module-level for Streamlit cache safety)."""
    service.run(service.integration.client.users.upsert_user(identifier=user_id))


async def _user_entity_ids(client: Any, user_id: str) -> set[str]:
    rows = await client.query.cypher(USER_ENTITY_IDS, {"user_id": user_id})
    return {row["id"] for row in rows}


async def _user_similar_traces(
    client: Any,
    user_id: str,
    query: str,
    *,
    limit: int = 5,
) -> list[dict[str, Any]]:
    traces = await client.reasoning.get_similar_traces(query, limit=limit * 3)
    if not traces:
        return []

    rows = await client.query.cypher(
        """
        MATCH (u:User {identifier: $user_id})-[:HAS_TRACE]->(rt:ReasoningTrace)
        RETURN rt.id AS id
        """,
        {"user_id": user_id},
    )
    allowed = {row["id"] for row in rows}
    return [
        {
            "id": str(trace.id),
            "task": trace.task,
            "outcome": trace.outcome,
            "success": trace.success,
        }
        for trace in traces
        if str(trace.id) in allowed
    ][:limit]
