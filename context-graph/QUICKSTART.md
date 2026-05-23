# Quick Start Guide

Get the Context Graph Explorer running in 5 minutes.

## Step 1: Start Neo4j

Using Docker (recommended):
```bash
docker run -d --name neo4j-instance \
  -p 7687:7687 \
  -p 7474:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

Or download from [neo4j.com](https://neo4j.com/download/)

## Step 2: Setup Python Environment

```bash
# From MedBrain repo root
cd context-graph

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
GOOGLE_API_KEY=your-gemini-api-key
```

Get your free Gemini API key at: https://aistudio.google.com/apikey

## Step 4: Load Sample Data (Optional)

```bash
python init_sample_data.py
```

This creates a sample knowledge graph with:
- 8 nodes (People, Organizations, Locations, Events, Objects)
- 10 relationships showing different connection types
- Full-text search indexes

## Step 5: Run the App

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

## First Queries to Try

### In Chat Tab:
- "Show me all people and their organizations"
- "Who works at TechCorp?"
- "What events is Alice Johnson attending?"

### In Search Tab:
- Search for "Alice" → Click "Show relationships"
- Search for "Conference" → Explore results

### In Query Editor:
```cypher
MATCH (n) RETURN n LIMIT 5
```

## Troubleshooting

### Neo4j Won't Connect
```bash
# Check if Neo4j is running
curl http://localhost:7474

# View Docker logs
docker logs neo4j-instance

# Restart Docker container
docker restart neo4j-instance
```

### Gemini API Error
- Get free API key at: https://aistudio.google.com/apikey
- Verify API key is set: `echo $GOOGLE_API_KEY`
- Test key: `python -c "import google.generativeai; google.generativeai.configure(api_key='your-key')"`

### Streamlit Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Reinstall
pip install --upgrade streamlit
```

## Next Steps

1. **Load your own data**: Modify `init_sample_data.py` or use Neo4j's import tools
2. **Customize agents**: Edit `_setup_tools()` in `langchain_agent.py`
3. **Add more pages**: Extend `app.py` with domain-specific views
4. **Deploy**: Use Streamlit Cloud or self-host

## Getting Help

- Neo4j: https://neo4j.com/docs/
- LangChain: https://python.langchain.com/
- Streamlit: https://docs.streamlit.io/
- Issues: Create an issue in the project repo

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Streamlit UI (app.py)           │
├─────────────────────────────────────────┤
│                                         │
│  Chat Interface  │  Search  │  Query    │
│  Statistics      │  Editor              │
│                                         │
├──────────────────┬──────────────────────┤
│  LangChain Agent │  Neo4j Utils         │
│  (4 core tools)  │  (Query execution)   │
├──────────────────┴──────────────────────┤
│                                         │
│         Neo4j Database                  │
│     (Knowledge Graph Storage)           │
│                                         │
└─────────────────────────────────────────┘
```

## Architecture Highlights

✓ **JSON Serialization**: All tool outputs use `json.dumps()` to handle Neo4j types  
✓ **Domain Isolation**: Nodes tagged with `domain` property for multi-tenant support  
✓ **Conversation Memory**: Chat maintains context across multiple turns  
✓ **Extensible Tools**: Easy to add custom tools and agent capabilities
