# MedBrain

Healthcare AI workspace.

## Projects

| Directory | Stack | Description |
|-----------|-------|-------------|
| [`radiology-analysis/`](radiology-analysis/) | TypeScript | Radiology analysis application |
| [`context-graph/`](context-graph/) | Python, Streamlit, Neo4j | Context graph explorer powered by [neo4j-agent-memory](https://github.com/neo4j-labs/agent-memory) |

## Context graph (quick start)

```bash
cd context-graph
uv venv .venv && uv pip install -r requirements.txt
cp .env.example .env   # set NEO4J_* and GOOGLE_API_KEY
streamlit run app.py
```

See [`context-graph/README.md`](context-graph/README.md) and [`context-graph/QUICKSTART.md`](context-graph/QUICKSTART.md) for full setup.

## Contributing

Open pull requests against [`mochiyaki/MedBrain`](https://github.com/mochiyaki/MedBrain) from your fork.
