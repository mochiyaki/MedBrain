import logging
import os
import uuid

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from context_memory import MemoryService, ensure_user_registered

# Bump when MemoryService API changes so @st.cache_resource reloads.
_MEMORY_SERVICE_VERSION = "per-user-v2"
from langchain_agent import ContextGraphAgent
from neo4j_utils import Neo4jConnector

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Context Graph Explorer", layout="wide", initial_sidebar_state="expanded")


@st.cache_resource
def init_neo4j():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    database = os.getenv("NEO4J_DATABASE", "neo4j")

    try:
        connector = Neo4jConnector(uri, user, password, database)
        return connector
    except Exception as e:
        st.error(f"Failed to connect to Neo4j: {e}")
        st.info("Make sure Neo4j is running and credentials are correct in your .env file")
        return None


@st.cache_resource
def init_memory_service(_version: str = _MEMORY_SERVICE_VERSION):
    try:
        service = MemoryService()
        service.connect()
        return service
    except Exception as e:
        st.error(f"Failed to initialize neo4j-agent-memory: {e}")
        st.info(
            "Install extras: `uv pip install 'neo4j-agent-memory[sentence-transformers,litellm]'`"
        )
        return None


@st.cache_resource
def init_agent(_memory: MemoryService, model: str, user_id: str, session_id: str):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("GOOGLE_API_KEY not found in environment variables")
        st.info("Add GOOGLE_API_KEY to your .env file from https://aistudio.google.com/apikey")
        return None

    try:
        return ContextGraphAgent(
            _memory,
            api_key,
            user_id=user_id,
            session_id=session_id,
            model=model,
        )
    except Exception as e:
        st.error(f"Failed to initialize agent: {e}")
        return None


def ensure_user_state(memory: MemoryService) -> None:
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user-{uuid.uuid4().hex[:8]}"

    ensure_user_registered(memory, st.session_state.user_id)

    if "session_id" not in st.session_state:
        st.session_state.session_id = memory.get_session_id()


def main():
    st.title("🧠 Context Graph Explorer")
    st.markdown(
        "Each user gets a **private context graph** in Neo4j — conversations, extracted "
        "entities, and reasoning traces are scoped by user identity."
    )

    memory = init_memory_service()
    connector = init_neo4j()
    if not memory or not connector:
        st.stop()

    ensure_user_state(memory)

    with st.sidebar:
        st.header("User Workspace")
        user_input = st.text_input(
            "User ID",
            value=st.session_state.user_id,
            help="Use a stable ID per clinician or workspace (e.g. dr.foster@hospital.org).",
        )
        if user_input.strip() and user_input.strip() != st.session_state.user_id:
            st.session_state.user_id = user_input.strip()
            st.session_state.session_id = memory.get_session_id()
            st.session_state.messages = []
            ensure_user_registered(memory, st.session_state.user_id)
            st.cache_resource.clear()
            st.rerun()

        st.caption(f"User: `{st.session_state.user_id}`")
        st.caption(f"Session: `{st.session_state.session_id[:8]}…`")

        st.header("Configuration")
        page = st.radio(
            "Select View",
            ["Chat", "Memory Graph", "Search", "Graph Statistics", "Query Editor"],
            label_visibility="collapsed",
        )

        if st.button("🔄 Refresh Connection"):
            st.cache_resource.clear()
            st.rerun()

        if st.button("🏥 Seed Healthcare Memory"):
            with st.spinner("Extracting entities for this user…"):
                n = memory.bootstrap_healthcare(user_id=st.session_state.user_id)
            st.success(f"Stored {n} bootstrap messages for `{st.session_state.user_id}`")
            st.cache_resource.clear()
            st.rerun()

        if st.button("🆕 New Session"):
            st.session_state.session_id = memory.get_session_id()
            st.session_state.messages = []
            st.cache_resource.clear()
            st.rerun()

        if st.button("👤 New User"):
            st.session_state.user_id = f"user-{uuid.uuid4().hex[:8]}"
            st.session_state.session_id = memory.get_session_id()
            st.session_state.messages = []
            ensure_user_registered(memory, st.session_state.user_id)
            st.cache_resource.clear()
            st.rerun()

    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

    if page == "Chat":
        chat_page(memory, model)
    elif page == "Memory Graph":
        memory_page(memory)
    elif page == "Search":
        search_page(connector)
    elif page == "Graph Statistics":
        stats_page(connector, memory)
    elif page == "Query Editor":
        query_editor_page(connector)


def chat_page(memory: MemoryService, model: str):
    st.header("💬 Context Graph Chat")
    st.markdown(
        f"Chatting as **`{st.session_state.user_id}`**. Messages and extracted entities "
        "stay in this user's private graph."
    )

    agent = init_agent(
        memory,
        model,
        st.session_state.user_id,
        st.session_state.session_id,
    )
    if not agent:
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("Ask about patients, providers, or add new clinical facts…"):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking (memory + reasoning)…"):
                response = agent.query(prompt)
                st.write(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.session_id = agent.reset_memory()
        st.cache_resource.clear()
        st.rerun()


def memory_page(memory: MemoryService):
    st.header("🕸️ Memory Graph")
    st.markdown(
        f"Visualization of **{st.session_state.user_id}**'s context graph "
        "(messages, entities, traces)."
    )

    user_id = st.session_state.user_id
    session_id = st.session_state.session_id
    stats = memory.get_stats(user_id=user_id, session_id=session_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entities (this user)", stats.get("entities", 0))
    c2.metric("Messages (this user)", stats.get("messages", 0))
    c3.metric("Reasoning traces", stats.get("reasoning_traces", 0))
    c4.metric("This session messages", stats.get("messages_in_session", 0))

    st.divider()

    try:
        graph = memory.export_graph(user_id=user_id, session_id=session_id)
        nodes = graph.get("nodes", [])
        rels = graph.get("relationships", [])

        if not nodes:
            st.info(
                "No memory graph nodes yet for this user. Use **Seed Healthcare Memory** "
                "in the sidebar, or chat to add facts — entities are extracted automatically."
            )
            return

        st.subheader("Nodes")
        node_rows = [
            {
                "id": n.get("id"),
                "labels": ", ".join(n.get("labels", [])),
                "name": n.get("properties", {}).get("name")
                or n.get("properties", {}).get("content", "")[:80],
            }
            for n in nodes[:100]
        ]
        st.dataframe(pd.DataFrame(node_rows), use_container_width=True)

        st.subheader("Relationships")
        rel_rows = [
            {
                "type": r.get("type"),
                "from": r.get("from_node"),
                "to": r.get("to_node"),
            }
            for r in rels[:100]
        ]
        st.dataframe(pd.DataFrame(rel_rows), use_container_width=True)

    except Exception as e:
        st.error(f"Could not export memory graph: {e}")


def search_page(connector):
    st.header("🔍 Legacy Graph Search")
    st.caption("Searches manually seeded nodes (Patient, Provider, etc.) from init scripts.")

    search_query = st.text_input("Enter search term (name or description):")

    if search_query:
        with st.spinner("Searching..."):
            results = connector.search_nodes(search_query, limit=20)

        if results:
            st.success(f"Found {len(results)} results")

            for idx, node in enumerate(results, 1):
                with st.expander(f"Result {idx}: {node.get('name', 'Unknown')}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Labels:**")
                        st.write(node.get("labels", []))

                    with col2:
                        st.write("**Name:**")
                        st.write(node.get("name", "N/A"))

                    st.write("**Description:**")
                    st.write(node.get("description", "N/A"))

                    if st.button(f"Show relationships for {node.get('name')}", key=f"btn_{idx}"):
                        rels = connector.get_relationships(node.get("name"))
                        if rels:
                            st.dataframe(rels)
                        else:
                            st.info("No relationships found")
        else:
            st.info("No results found")


def stats_page(connector, memory: MemoryService):
    st.header("📊 Graph Statistics")

    st.subheader(f"Context graph for `{st.session_state.user_id}`")
    mem_stats = memory.get_stats(
        user_id=st.session_state.user_id,
        session_id=st.session_state.session_id,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Memory entities", mem_stats.get("entities", 0))
    c2.metric("Memory messages", mem_stats.get("messages", 0))
    c3.metric("Reasoning traces", mem_stats.get("reasoning_traces", 0))
    c4.metric("Session messages", mem_stats.get("messages_in_session", 0))

    st.divider()
    st.subheader("Legacy knowledge graph (manual seed scripts)")

    try:
        stats = connector.get_graph_stats()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Nodes", stats.get("nodes", 0))

        with col2:
            st.metric("Total Relationships", stats.get("relationships", 0))

        with col3:
            st.metric("Graph Labels", stats.get("label_count", 0))

        st.json(stats)

    except Exception as e:
        st.error(f"Error fetching statistics: {e}")


def query_editor_page(connector):
    st.header("⚙️ Cypher Query Editor")
    st.markdown("Execute custom Cypher queries against your Neo4j database")

    col1, col2 = st.columns([4, 1])

    with col1:
        cypher_query = st.text_area(
            "Enter Cypher query:",
            placeholder="MATCH (u:User {identifier: $user_id}) RETURN u",
            height=200,
        )

    with col2:
        st.write("")
        st.write("")
        execute_btn = st.button("Execute", type="primary")

    if execute_btn and cypher_query:
        with st.spinner("Executing query..."):
            try:
                results = connector.query(cypher_query)

                st.success(f"Query executed successfully. Got {len(results)} results.")

                if results:
                    st.dataframe(results)
                else:
                    st.info("Query returned no results")

            except Exception as e:
                st.error(f"Query error: {str(e)}")


if __name__ == "__main__":
    main()
