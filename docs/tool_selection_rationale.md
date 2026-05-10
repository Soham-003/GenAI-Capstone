# Tool Selection Rationale

This document explains why each major tool was selected for this project and why common alternatives were not used in the first version.

## 1) Vector Database: ChromaDB

### Why selected
- Simple setup for local and demo environments.
- Good developer ergonomics for Python-based RAG prototypes.
- Supports persistent local collections without infrastructure overhead.

### Why not Pinecone/Weaviate/Qdrant now
- Managed services add cost and operational setup not required for MVP evaluation.
- Goal is fast iteration on retrieval quality before scaling infrastructure choices.

## 2) UI: Streamlit

### Why selected
- Very fast way to deliver a usable chat interface and controls.
- Ideal for stakeholder demos and iteration with data teams.
- Minimal frontend engineering required.

### Why not React/Next.js now
- More production-grade for custom UX, but slower to implement for this capstone scope.

## 3) API Layer: FastAPI

### Why selected
- Clear separation between UI and backend business logic.
- Async-ready and production-friendly with strong typing and validation.
- Easy to containerize and integrate with CI.

### Why not Flask now
- FastAPI provides stricter typing and modern API ergonomics by default.

## 4) LLM Backend: OpenAI API

### Why selected
- Strong quality for reasoning and summarization tasks.
- Mature SDK and clear operational patterns for retries, safety, and monitoring.
- Easy adoption by teams already using OpenAI ecosystem.

### Why not Claude in this version
- Requirement updated to OpenAI key availability.
- Keeping one LLM backend simplifies governance, cost tracking, and incident troubleshooting.

## 5) Tool Integration Standard: MCP

### Why selected
- Decouples agent orchestration from tool implementations.
- Makes it easier to add enterprise tools later (Snowflake, Postgres, catalog APIs).
- Reduces vendor lock-in for tool-calling interfaces.

## 6) Monitoring: Prometheus + Grafana

### Why selected
- Industry-standard open observability stack.
- Covers core SRE/ops needs: request volume, latency, action execution counts.
- Easy to present reliability posture in demos and reviews.

### Why not Datadog/New Relic now
- Great managed platforms, but not necessary for initial architecture validation.

## 7) Testing: Pytest

### Why selected
- Widely used in Python ecosystems.
- Clean syntax for unit and integration tests.
- Strong plugin ecosystem for coverage and CI integration.
