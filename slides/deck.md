# Slide 1 - Title
Data Engineer Conversational Assistant  
RAG + OpenAI + MCP + Agentic Action + Observability

# Slide 2 - Problem
- Fragmented access to pipeline docs, metadata, and incident state
- Slow root-cause analysis during failures
- Inconsistent governance checks

# Slide 3 - Objectives
- Conversational Q&A over codebase and catalogue
- Health + SLO visibility from one interface
- Trigger operational actions from chat

# Slide 4 - Architecture
- Retrieve -> Augment -> Generate (RAG)
- ChromaDB vector search over docs + metadata
- OpenAI for reasoning and response generation
- MCP for tool integration

# Slide 5 - Data Sources
- Pipeline design docs
- Data catalogue extracts (tables, tags, lineage)
- Pipeline health snapshots (status, failures, SLO)

# Slide 6 - Agentic Workflow
- User asks for action (quality check)
- Assistant invokes tool/action layer
- Returns result + recommendation

# Slide 7 - Dashboarding
- Prometheus metrics endpoint from assistant
- Grafana dashboard for request rate, action count, p95 latency
- Supports incident-time visibility and trends

# Slide 8 - Security and Governance
- PII-aware responses using metadata tags
- Principle of least privilege for MCP tools
- Audit-friendly traceability via citations

# Slide 9 - Testing and Quality
- Unit tests for chunking, actions, and chat orchestration
- Deterministic mock mode without external API
- Extendable to integration tests and CI gates

# Slide 10 - Demo and Roadmap
- Live app: Streamlit chat + FastAPI backend
- Notebook: end-to-end walkthrough
- Next: hybrid search, lineage graph view, self-healing actions
