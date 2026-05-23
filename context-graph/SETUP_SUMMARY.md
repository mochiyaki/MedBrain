# Context Graph Explorer - Setup Complete ✅

A production-ready Streamlit application for exploring Neo4j knowledge graphs using LangChain agents.

## Project Structure

```
context-graph/
├── 📄 README.md                    # Main documentation
├── 🚀 QUICKSTART.md               # 5-minute setup guide
├── 📋 SETUP_SUMMARY.md            # This file
│
├── 🎨 Frontend & UI
│   └── app.py                      # Main Streamlit application (4 pages)
│
├── 🔌 Core Integrations
│   ├── neo4j_utils.py              # Neo4j connection & query layer
│   ├── langchain_agent.py          # LangChain ReAct agent with 4 tools
│   └── graph_utils.py              # Graph analysis & visualization
│
├── 🛠️ Utilities & Data
│   ├── init_sample_data.py         # Initialize sample knowledge graph
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Environment template
│
└── 📚 Documentation
    └── .claude/skills/
        └── create-context-graph.md # Project architecture & patterns
```

## Core Components Explained

### 1. **app.py** (Streamlit UI)
Main entry point with 4 interactive pages:

| Page | Features |
|------|----------|
| **Chat** | Natural language queries using LangChain agent with conversation memory |
| **Search** | Full-text search across nodes with relationship exploration |
| **Graph Statistics** | Dashboard showing graph metrics and structure |
| **Query Editor** | Execute custom Cypher queries directly |

**Key Features:**
- Session state management for chat history
- Resource caching for Neo4j connections
- Error handling and user feedback
- Responsive multi-column layouts

### 2. **neo4j_utils.py** (Database Layer)
Neo4j connection abstraction with high-level query methods:

```python
# Initialize
connector = Neo4jConnector(uri, user, password)

# Query methods
results = connector.search_nodes(query)        # Full-text search
rels = connector.get_relationships(node_name)  # Find connections
stats = connector.get_graph_stats()            # Graph metrics
```

**Implements:**
- Connection pooling and lifecycle management
- JSON serialization for Neo4j types (matches create-context-graph patterns)
- Context manager support (`with` statements)

### 3. **langchain_agent.py** (AI Agent)
LangChain ReAct agent with specialized Neo4j tools:

```python
# 4 Core Tools
- search_nodes()      # Find nodes by name/description
- get_relationships() # Explore node connections
- query_graph()       # Execute Cypher queries
- get_insights()      # Graph statistics
```

**Features:**
- OpenAI function calling for reliable tool selection
- Conversation memory for multi-turn interactions
- Error handling and graceful degradation

### 4. **graph_utils.py** (Analysis & Visualization)
Graph analysis and interactive visualization:

```python
analyzer = GraphAnalyzer(connector)

# Analysis methods
subgraph = analyzer.get_subgraph(node_name, hops=1)
paths = analyzer.find_shortest_path(source, target)
density = analyzer.get_graph_density()

# Visualization
fig = analyzer.create_plotly_network(node_name)
```

### 5. **init_sample_data.py** (Data Initialization)
Creates sample knowledge graph following POLE+O model:

- **8 Sample Nodes**: Person, Organization, Location, Event, Object
- **10 Relationships**: WORKS_AT, LOCATED_IN, KNOWS, ATTENDING, CREATED
- **Full-Text Indexes**: Fast search across nodes
- **Constraints**: Unique node names for data integrity

Run once to populate Neo4j:
```bash
python init_sample_data.py
```

## Architecture & Design Patterns

### Design Patterns (from create-context-graph)

1. **JSON Serialization Convention**
   - All agent tools return JSON strings via `json.dumps(result, default=str)`
   - Ensures Neo4j-specific types serialize correctly

2. **Domain Isolation**
   - Nodes tagged with `domain` property
   - Enables multi-tenant data separation in shared Neo4j instances

3. **Tool Return Convention**
   - Consistent JSON output format
   - Error handling with wrapped exception objects
   - Type safety for downstream processing

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | Streamlit | Interactive web interface |
| Agent | LangChain | ReAct agent with tool calling |
| Database | Neo4j | Graph database backend |
| LLM | Google Gemini 3.5 Flash | Natural language processing |
| Visualization | Plotly | Interactive network graphs |
| Utilities | NetworkX | Graph analysis algorithms |

## Setup Instructions

### Prerequisites
- Python 3.8+
- Neo4j (Docker or standalone)
- OpenAI API key

### Installation (5 minutes)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Start Neo4j (Docker)
docker run -d --name neo4j \
  -p 7687:7687 -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# 5. Initialize sample data
python init_sample_data.py

# 6. Run application
streamlit run app.py
```

## API Reference

### Neo4jConnector
```python
# Connection
connector = Neo4jConnector(uri, user, password)

# Queries
results = connector.query(cypher, parameters)
stats = connector.execute(cypher, parameters)

# Search
nodes = connector.search_nodes(query, limit=10)
rels = connector.get_relationships(node_name)

# Context manager
with Neo4jConnector(...) as conn:
    results = conn.query("MATCH (n) RETURN n")
```

### ContextGraphAgent
```python
# Initialize
agent = ContextGraphAgent(connector, api_key, model="gpt-3.5-turbo")

# Query
response = agent.query("Find all people at TechCorp")

# Memory
agent.reset_memory()
```

### GraphAnalyzer
```python
# Initialize
analyzer = GraphAnalyzer(connector)

# Analysis
subgraph = analyzer.get_subgraph(node_name, hops=2)
paths = analyzer.find_shortest_path(source, target)
degree = analyzer.get_node_degree(node_name)
density = analyzer.get_graph_density()

# Visualization
fig = analyzer.create_plotly_network(node_name, hops=1)
```

## Configuration

### Environment Variables (.env)
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
GOOGLE_API_KEY=your_gemini_api_key
```

Get your free Gemini API key at: https://aistudio.google.com/apikey

### Neo4j Connection Options
- **Local**: `bolt://localhost:7687`
- **Cloud**: `neo4j+s://your-instance`
- **Secure**: `bolt+ssc://...`

### LLM Model Selection
```python
# In langchain_agent.py, modify:
# Use different Gemini models
self.llm = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-3.5-pro")  # For Pro version
self.llm = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-pro")      # For Pro 1.5
```

Available models (as of May 2026):
- `gemini-3.5-flash` - Fastest, cheapest, recommended (latest)
- `gemini-3.5-pro` - More capable (coming soon)
- `gemini-pro-vision` - With image understanding

## Extending the Application

### Adding Custom Tools
Edit `_setup_tools()` in `langchain_agent.py`:
```python
def _setup_tools(self):
    tools = super()._setup_tools()
    
    tools.append(Tool(
        name="my_tool",
        func=self._my_function,
        description="What this does"
    ))
    
    return tools
```

### Adding New Pages
In `app.py`:
```python
if page == "Custom Page":
    custom_page(connector)

def custom_page(connector):
    st.header("My Custom Page")
    # Your Streamlit code here
```

### Custom Cypher Queries
Access directly via Neo4j utils:
```python
results = connector.query("""
    MATCH (n:Person)-[r:KNOWS]->(m:Person)
    RETURN n.name, m.name, type(r)
""")
```

## Troubleshooting

### Common Issues

**Connection Error**
```bash
# Verify Neo4j is running
curl http://localhost:7474

# Check credentials in .env
# Restart container if needed
docker restart neo4j
```

**LLM Errors**
- Verify OPENAI_API_KEY is set
- Check account has sufficient credits
- Test: `python -c "import openai; print(openai.__version__)"`

**Query Timeouts**
- Add `LIMIT` clauses for large graphs
- Create indexes on frequently searched properties
- Check Neo4j logs: `docker logs neo4j`

## Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

### Environment Variables for Production
```bash
# Use secrets management
export NEO4J_URI="..."
export NEO4J_USER="..."
export NEO4J_PASSWORD="..."
export GOOGLE_API_KEY="..."
```

### Streamlit Cloud Deployment
1. Push code to GitHub
2. Connect at streamlit.io/cloud
3. Configure secrets in app settings
4. Deploy

## Performance Optimization

### Neo4j Optimization
```cypher
-- Create indexes for better performance
CREATE INDEX idx_node_name FOR (n) ON (n.name);
CREATE INDEX idx_node_domain FOR (n) ON (n.domain);

-- Use EXPLAIN to analyze queries
EXPLAIN MATCH (n) WHERE n.name CONTAINS $query RETURN n;
```

### Streamlit Optimization
- Use `@st.cache_resource` for expensive operations
- Limit result sets with `LIMIT` clauses
- Consider pagination for large datasets

## Security Considerations

- ✅ Use environment variables for credentials (never hardcode)
- ✅ Implement authentication for production deployments
- ✅ Validate all user input in Cypher queries
- ✅ Use connection pooling for database access
- ✅ Sanitize LLM inputs to prevent injection

## Next Steps

1. **Try the Quick Start**: Follow [QUICKSTART.md](QUICKSTART.md)
2. **Load Your Data**: Modify `init_sample_data.py` for your domain
3. **Customize Tools**: Add domain-specific tools to the agent
4. **Deploy**: Follow production deployment guide above
5. **Monitor**: Set up logging and monitoring for production

## Documentation References

- [create-context-graph Skills](.claude/skills/create-context-graph.md)
- [Streamlit Docs](https://docs.streamlit.io/)
- [LangChain Docs](https://python.langchain.com/)
- [Neo4j Docs](https://neo4j.com/docs/)
- [Google Gemini API](https://ai.google.dev/)
- [Get Gemini API Key](https://aistudio.google.com/apikey)

## Support & Contributions

For issues or questions:
1. Check troubleshooting section
2. Review Neo4j/LangChain/Streamlit documentation
3. Check application logs: `streamlit run app.py --logger.level=debug`

---

**Version**: 1.0  
**Last Updated**: 2026-05-23  
**Status**: ✅ Production Ready
