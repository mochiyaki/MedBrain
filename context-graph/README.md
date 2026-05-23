# Context Graph Explorer

A Streamlit application for exploring Neo4j **context graphs** using [neo4j-agent-memory](https://github.com/neo4j-labs/agent-memory) and LangChain (Gemini 3.5 Flash).

## Features

- **Per-user context graphs** — each clinician/workspace gets isolated memory in Neo4j
- **Three memory layers** — short-term (messages), long-term (entities), reasoning (traces)
- **Auto entity extraction** from chat and seeded clinical narratives
- **Memory Graph viewer** — inspect messages, entities, and relationships
- **Legacy Cypher tools** — search manually seeded healthcare nodes, run custom queries

## Architecture

### Core components

| File | Role |
|------|------|
| `context_memory.py` | Wraps neo4j-agent-memory (Streamlit-safe async thread) |
| `langchain_agent.py` | LangChain agent with memory tools + reasoning traces |
| `neo4j_utils.py` | Direct Neo4j queries for legacy seed data |
| `app.py` | Streamlit UI |

Memory tools: `memory_search`, `memory_get_context`, `memory_search_entities`.

## Setup

### Prerequisites

- Python 3.8+
- Neo4j database (local or remote)
- Google Gemini API key

### Installation

1. From the MedBrain repo root:

```bash
cd context-graph
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
GOOGLE_API_KEY=your_gemini_api_key
```

Get your Gemini API key at [Google AI Studio](https://aistudio.google.com/apikey)

### Running Neo4j Locally

Using Docker:
```bash
docker run -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

Then access Neo4j Browser at http://localhost:7474

### Running the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Usage

### Chat Interface

Ask natural language questions about your graph:
- "What are the relationships between [Node A] and [Node B]?"
- "Find all organizations connected to [Person Name]"
- "Show me the structure of entities related to [Event]"

The LangChain agent will select appropriate tools and execute queries automatically.

### Search

Use the search page to:
- Find nodes by name or description
- View node properties
- Explore relationships from any node

### Graph Statistics

View:
- Total node count
- Total relationship count
- Graph labels/ontologies
- Database summary

### Query Editor

Execute custom Cypher queries for advanced exploration:
```cypher
MATCH (n:Person)-[r:KNOWS]->(m:Person)
RETURN n.name, m.name, type(r)
```

## Design Patterns (from create-context-graph)

### Tool Return Convention
All agent tools return JSON-serialized strings using `json.dumps(result, default=str)` to ensure Neo4j-specific types serialize correctly.

### Domain Isolation
Entities are tagged with domain properties enabling secure multi-tenant data separation within shared Neo4j instances.

### Thread-Safe Async Bridging
The LangChain agent uses OpenAI's function calling for reliable execution without explicit async management.

## Configuration

### Neo4j Connection

Supported URI formats:
- `bolt://localhost:7687` - Direct connection
- `neo4j+s://your-cloud-instance` - Secure cloud connection
- `bolt+ssc://` - Bolt with SSL

### LLM Models

The agent uses **Gemini 3.5 Flash** by default. To use different Gemini models:

```python
# In langchain_agent.py
self.llm = ChatGoogleGenerativeAI(api_key=llm_api_key, model="gemini-pro")
```

Available Gemini models:
- `gemini-3.5-flash` (latest, fastest, recommended)
- `gemini-3.5-pro` (coming soon, more capable)
- `gemini-pro` (previous version)
- `gemini-pro-vision` (with image understanding)

## Extending the Agent

Add custom tools by modifying `_setup_tools()` in `ContextGraphAgent`:

```python
def _setup_tools(self) -> list:
    tools = super()._setup_tools()
    
    # Add custom tool
    tools.append(Tool(
        name="my_custom_tool",
        func=self._my_custom_function,
        description="What this tool does"
    ))
    
    return tools
```

## Troubleshooting

**Connection Error**: Ensure Neo4j is running and credentials are correct
```bash
# Test connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))"
```

**LLM Errors**: Verify GOOGLE_API_KEY is set and has sufficient quota at [Google AI Studio](https://aistudio.google.com/apikey)

**Query Timeouts**: For large graphs, consider adding LIMIT clauses or use indexes

## Project Structure

```
context-graph/
├── app.py                 # Streamlit main app
├── neo4j_utils.py        # Neo4j connection and queries
├── langchain_agent.py    # LangChain agent with tools
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .claude/
│   └── skills/
│       └── create-context-graph.md  # Project skills documentation
└── README.md
```

## Related Documentation

- [create-context-graph Skills](.claude/skills/create-context-graph.md)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
