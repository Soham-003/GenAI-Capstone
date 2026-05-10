# Data Engineer Assistant: Complete Beginner's Guide

## Welcome! 👋

Welcome to the Data Engineer Conversational Assistant! This guide will walk you through everything you need to know about this project, from basic concepts to advanced usage. Whether you're new to data engineering or just want to understand this specific system, this guide has you covered.

---

## Table of Contents

1. [What This Project Does](#what-this-project-does)
2. [How It All Works Together](#how-it-all-works-together)
3. [The Data Pipeline Explained](#the-data-pipeline-explained)
4. [The Chat Assistant](#the-chat-assistant)
5. [Grafana Dashboard Deep Dive](#grafana-dashboard-deep-dive)
6. [Step-by-Step Setup](#step-by-step-setup)
7. [Using the System](#using-the-system)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Topics](#advanced-topics)

---

## What This Project Does

Imagine you're a data engineer working at a company. You have:
- **Data pipelines** that process customer data, transactions, and products
- **Complex codebases** with lots of documentation
- **Monitoring dashboards** to keep everything running smoothly
- **Questions from stakeholders** about data and pipelines

This project gives you an AI assistant that can help with all of this! It combines:

1. **Conversational AI** - Ask questions in plain English
2. **Data Pipeline Monitoring** - Real-time health and performance tracking
3. **Data Catalogue Exploration** - Find and understand your data assets
4. **Automated Actions** - Trigger quality checks and pipeline operations

---

## How It All Works Together

Think of this system as a data engineer's best friend with four main capabilities:

### 🗣️ Chat Assistant (Streamlit UI)
- **What**: A chat interface where you can ask questions
- **How**: Uses AI to understand your questions and provide answers
- **Data Source**: Searches through your code, documentation, and data

### 🔄 Data Pipeline (Bronze → Silver → Gold)
- **What**: Processes raw data into business insights
- **How**: Automated transformations with quality checks
- **Purpose**: Turns messy data into clean, useful information

### 📊 Monitoring Dashboard (Grafana)
- **What**: Visual dashboard showing system health
- **How**: Real-time metrics and alerts
- **Purpose**: Know instantly if something goes wrong

### 📋 Data Catalogue
- **What**: Inventory of all your data tables and relationships
- **How**: Automatically discovers and maps data lineage
- **Purpose**: Understand what data you have and how it flows

---

## The Data Pipeline Explained

### Why "Bronze-Silver-Gold"?

This follows the **medallion architecture** - a common pattern in data engineering:

```
Bronze (Raw) → Silver (Clean) → Gold (Insights)
```

### Bronze Layer: Raw Data Landing Zone

**Purpose**: Store data exactly as it comes from sources
**Characteristics**:
- No transformations applied
- Preserves original data quality
- Acts as historical archive

**Example Data**:
```
Customer ID: 12345
Email: john.doe@email.com
Signup Date: 2023-01-15
Income: 75000
Country: USA
```

**What happens here**: Data gets ingested from various sources (APIs, files, databases) and stored as-is.

### Silver Layer: Data Cleansing & Enrichment

**Purpose**: Clean, standardize, and add business logic
**Characteristics**:
- Data quality improvements
- Business rules applied
- Ready for analysis

**Transformations Applied**:
- **Customer Data**: Extract email domains, create age groups, segment by income
- **Transaction Data**: Add time features (day of week, quarter, weekend flags)
- **Product Data**: Categorize by price range, calculate performance metrics

**Example Output**:
```
Customer ID: 12345
Email Domain: email.com
Age Group: 25-34
Income Tier: Medium
Country: USA
Signup Month: 1
Signup Year: 2023
```

### Gold Layer: Business Intelligence

**Purpose**: Aggregated insights for decision-making
**Characteristics**:
- Summarized data
- KPI calculations
- Optimized for reporting

**Business Insights Created**:
- **Customer Segmentation**: Revenue by customer groups
- **Monthly Performance**: Sales trends, success rates
- **Product Analytics**: Best-selling categories, performance metrics

---

## The Chat Assistant

### What Can You Ask?

The assistant understands natural language and can help with:

#### Pipeline Questions
- "How does the customer segmentation work?"
- "What transformations happen in the silver layer?"
- "Show me the data flow from bronze to gold"

#### Data Exploration
- "What tables contain customer data?"
- "Show me data lineage for the transactions table"
- "Which tables have PII data?"

#### Health & Monitoring
- "Is the pipeline running successfully?"
- "What was the last pipeline execution time?"
- "Are there any data quality issues?"

#### Actions
- "Run a quality check on the gold layer"
- "Execute the full data pipeline"
- "Scan the data catalogue"

### How It Finds Answers

1. **Vector Search**: Converts your question into a mathematical vector
2. **Similarity Matching**: Finds similar content in the knowledge base
3. **Context Retrieval**: Gets relevant code, docs, and data examples
4. **AI Generation**: Uses GPT-4 to craft a helpful response

### Knowledge Base Includes

- **Code**: All Python files and their comments
- **Documentation**: Pipeline design docs, data dictionaries
- **Data Samples**: Example records from each layer
- **API Documentation**: Endpoint descriptions and schemas

---

## Grafana Dashboard Deep Dive

### Dashboard Overview

The Grafana dashboard is your **mission control center**. It shows the health and performance of your entire data ecosystem at a glance.

### Panel-by-Panel Breakdown

#### 🚀 Pipeline Health Status
- **Location**: Top left
- **What it shows**: Is your pipeline healthy?
- **How it works**:
  - 🟢 Green = Everything working perfectly
  - 🔴 Red = There are problems
- **Updates**: Refreshes every 10 seconds
- **Why it matters**: Instant alert if something breaks

#### 📊 Total Pipeline Executions
- **Location**: Top center
- **What it shows**: How many times the pipeline has run
- **Example**: "47" means the pipeline ran 47 times
- **Why it matters**: Shows pipeline activity and usage

#### ✅ Pipeline Success Rate
- **Location**: Top right
- **What it shows**: What percentage of runs succeed
- **Calculation**: (Successful runs ÷ Total runs) × 100
- **Target**: Should be 95% or higher
- **Why it matters**: Measures pipeline reliability

#### ⏱️ Pipeline Performance (P50, P95, P99)
- **Location**: Second row, left
- **What it shows**: How long pipeline runs take
- **P50**: 50% of runs complete in this time or less
- **P95**: 95% of runs complete in this time or less
- **P99**: 99% of runs complete in this time or less
- **Why it matters**: Identifies performance bottlenecks

#### 🔄 Layer Transformations
- **Location**: Second row, center
- **What it shows**: Activity breakdown by pipeline layer
- **Tracks**: Bronze→Silver and Silver→Gold transformations
- **Why it matters**: Shows which parts are most active

#### 📋 Data Catalogue Summary
- **Location**: Second row, right
- **What it shows**: Overview of your data inventory
- **Metrics**:
  - Tables Count: Total number of data tables
  - PII Tables: Tables with sensitive data
  - Lineage Relations: Data flow connections
- **Why it matters**: Understands your data landscape

#### 📈 Execution Rate (per minute)
- **Location**: Third row, left
- **What it shows**: How often the pipeline runs
- **Example**: "0.5/min" means pipeline runs twice per hour
- **Why it matters**: Monitors automation frequency

#### 🔍 Data Quality Scores
- **Location**: Third row, center
- **What it shows**: Quality score for each data layer
- **Scale**: 0-100 (100 = perfect quality)
- **Why it matters**: Ensures data meets quality standards

#### 🚨 Recent Failures
- **Location**: Third row, right
- **What it shows**: Pipeline failures in the last hour
- **Example**: "2" means 2 failures in the last hour
- **Why it matters**: Quick identification of issues

#### 📅 Last Execution Timestamp
- **Location**: Bottom row
- **What it shows**: When the pipeline last ran successfully
- **Format**: Human-readable timestamp
- **Why it matters**: Confirms pipeline is running on schedule

### Dashboard Features

#### Auto-Refresh
- **Frequency**: Every 10 seconds
- **Purpose**: Real-time monitoring
- **Benefit**: See issues as they happen

#### Color Coding
- **Green**: Everything is good
- **Red/Yellow**: Attention needed
- **Purpose**: Quick visual status assessment

#### Interactive Elements
- **Clickable Panels**: Click for detailed views
- **Time Range Selection**: View historical data
- **Refresh Button**: Manual data refresh

#### Alerting
- **Thresholds**: Automatic alerts on failures
- **Notifications**: Email/Slack integration possible
- **Escalation**: Different alert levels

---

## Step-by-Step Setup

### Prerequisites Check

Before starting, ensure you have:

1. **Python 3.11 or higher**
   ```bash
   python --version
   ```

2. **Docker and Docker Compose**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Git** (for cloning repositories)
   ```bash
   git --version
   ```

### Step 1: Get the Code

```bash
# Clone the repository
git clone <repository-url>
cd genai-capstone

# Or download and extract the ZIP file
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (optional - OpenAI key)
# OPENAI_API_KEY=your-key-here
```

### Step 4: Build Knowledge Base

```bash
# Index documentation and code
python -m app.rag.ingestion
```

This creates a searchable index of:
- All Python code and comments
- Documentation files
- Data samples and schemas

### Step 5: Start Monitoring Infrastructure (Optional)

```bash
# Start Prometheus and Grafana (optional)
docker-compose up -d

# Verify they're running
docker ps
```

### Step 6: Start the Application

```bash
# Start the complete Streamlit application
streamlit run app/ui/streamlit_app.py
```

The application will be available at: http://localhost:8501

### Step 7: Generate Initial Data (Optional)

```bash
# Generate sample data (demo data included)
python scripts/generate_demo_data.py
```

### Step 8: Explore the Application

1. **Main Application**: http://localhost:8501
   - 5 tabs: Chat Assistant, Pipeline Operations, Data Catalogue, Quality Checks, Monitoring Dashboard
2. **Grafana Dashboard** (if started): http://localhost:3000 (admin/admin)
3. **Prometheus** (if started): http://localhost:9090

---

## Using the System

### Basic Chat Usage

1. **Open the application** at http://localhost:8501
2. **Click the "💬 Chat Assistant" tab**
3. **Ask questions** in natural language:
   - "How does the pipeline work?"
   - "Show me customer data tables"
   - "What transformations happen in silver layer?"
4. **Choose response style**: Standard, Detailed, or Code Examples
5. **Enable quality checks** if you want data validation included

### Pipeline Operations

#### Execute Pipeline
1. **Click "🔄 Pipeline Operations" tab**
2. **Choose pipeline layer**: full, bronze-to-silver, or silver-to-gold
3. **Click "🚀 Execute Pipeline"**
4. **View execution results** and timing

#### Check Pipeline Status
1. **In Pipeline Operations tab**
2. **Click "📊 Check Status"**
3. **Review current health metrics**

#### Run Quality Validation
1. **In Pipeline Operations tab**
2. **Select target layer** (bronze/silver/gold)
3. **Click "🔍 Validate Quality"**

### Data Catalogue Operations

#### Scan for New Tables
1. **Click "📋 Data Catalogue" tab**
2. **Click "🔍 Scan Data Layers"**
3. **Wait for scan completion**

#### List All Tables
1. **In Data Catalogue tab**
2. **Click "📋 List All Tables"**
3. **Browse the table grid** with metadata

#### Search Tables
1. **In Data Catalogue tab**
2. **Use the search box** to find specific tables**
3. **Type table names or column names**

#### View Catalogue Summary
1. **In Data Catalogue tab**
2. **Scroll to "Catalogue Summary" section**
3. **See layer breakdown and PII statistics**

### Quality Checks

#### Run Comprehensive Quality Check
1. **Click "🔍 Quality Checks" tab**
2. **Click "🩺 Run Full Quality Assessment"**
3. **View overall quality score and issues**

#### Run Targeted Quality Actions
1. **In Quality Checks tab**
2. **Select action type**: comprehensive_check, validate_schemas, etc.
3. **Choose target layer**: all, bronze, silver, or gold
4. **Click "⚡ Run Action"**

#### Check Quality Status
1. **In Quality Checks tab**
2. **Click "📊 Get Quality Status"**
3. **Review current health indicators**

### Quality Checks

#### Run Comprehensive Quality Check
```bash
curl -X POST "http://localhost:8000/agents/quality/comprehensive"
```

#### Check Quality Status
```bash
curl "http://localhost:8000/agents/quality/status"
```

---

## Troubleshooting

### Common Issues and Solutions

#### "Command not found: python"
**Problem**: Python not installed or not in PATH
**Solution**:
```bash
# Check if Python is installed
which python3

# Use python3 instead
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[dev]"
```

#### "Port 8000 already in use"
**Problem**: Another service using the port
**Solution**:
```bash
# Find what's using the port
lsof -i :8000

# Kill the process or use different port
uvicorn app.api.main:app --port 8001
```

#### "Docker containers not starting"
**Problem**: Docker not running or permission issues
**Solution**:
```bash
# Start Docker service
sudo systemctl start docker  # Linux
# Or start Docker Desktop on Mac/Windows

# Check Docker status
docker ps
```

#### "Grafana dashboard shows no data"
**Problem**: Pipeline hasn't been executed yet
**Solution**:
```bash
# Execute pipeline to generate metrics
curl -X POST "http://localhost:8000/pipeline/execute"

# Wait 10-15 seconds, then refresh dashboard
```

#### "Chat responses are generic"
**Problem**: Knowledge base not indexed
**Solution**:
```bash
# Rebuild the index
python -m app.rag.ingestion
```

#### "OpenAI API errors"
**Problem**: Invalid or missing API key
**Solution**:
```bash
# Add to .env file
echo "OPENAI_API_KEY=your-actual-key" >> .env

# Restart the API server
```

### Getting Help

1. **Check logs**:
```bash
# API server logs (in terminal where uvicorn is running)
# Streamlit logs (in terminal where streamlit is running)
```

2. **Health checks**:
```bash
# API health
curl "http://localhost:8000/health"

# Metrics endpoint
curl "http://localhost:8001/metrics"
```

3. **Test individual components**:
```bash
# Run tests
pytest tests/ -v

# Test pipeline manually
python -c "from app.pipeline.processor import DataPipelineProcessor; p = DataPipelineProcessor(); print('Pipeline works!')"
```

---

## Advanced Topics

### Customizing the Pipeline

#### Adding New Data Sources

1. **Add raw data** to `data/docs/bronze/`
2. **Create transformation logic** in `app/pipeline/processor.py`
3. **Update the pipeline service** in `app/pipeline/service.py`

#### Modifying Transformations

Edit `app/pipeline/processor.py`:
- `_process_bronze_to_silver()`: Add new cleansing rules
- `_process_silver_to_gold()`: Add new aggregations
- `_create_customer_segmentation()`: Modify segmentation logic

### Extending the Chat Assistant

#### Adding New Knowledge Sources

1. **Add documents** to `data/docs/`
2. **Rebuild index**: `python -m app.rag.ingestion`
3. **Test queries** to ensure information is found

#### Customizing Responses

Edit `app/services/chat_service.py`:
- Modify system prompts
- Add custom response formatting
- Integrate additional tools

### Monitoring and Alerting

#### Adding New Metrics

Edit `app/observability/metrics.py`:
```python
# Add custom counter
self.custom_counter = Counter('custom_operations_total', 'Custom operations')

# Use in your code
self.custom_counter.inc()
```

#### Creating Dashboard Panels

1. **Edit** `infra/grafana/dashboards/data_pipeline_dashboard.json`
2. **Add new panel** with appropriate PromQL queries
3. **Restart Grafana** or refresh dashboard

### Integrating with External Systems

#### MCP Server Integration

The project includes MCP (Model Context Protocol) servers for extensibility:

- **Filesystem MCP**: Access local files and metadata
- **Custom MCP Servers**: Add in `mcp_servers/` directory

#### API Integration

The FastAPI backend makes it easy to integrate with:
- **Data warehouses** (Snowflake, BigQuery, Redshift)
- **Workflow orchestrators** (Airflow, Prefect, Dagster)
- **Monitoring systems** (DataDog, New Relic)
- **Communication tools** (Slack, Teams)

### Production Deployment

#### Docker Containerization

```bash
# Build API container
docker build -t de-assistant-api .

# Run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

#### Environment Configuration

- Use environment-specific `.env` files
- Configure proper logging and monitoring
- Set up backup and recovery procedures

#### Security Considerations

- Store secrets in environment variables
- Use HTTPS in production
- Implement proper authentication
- Regular security updates

---

## Key Concepts Summary

### Data Engineering Concepts
- **Medallion Architecture**: Bronze → Silver → Gold data layers
- **Data Lineage**: Tracking data flow through transformations
- **Data Quality**: Validation and monitoring of data integrity
- **ETL/ELT**: Extract, Transform, Load processes

### AI/ML Concepts
- **RAG (Retrieval-Augmented Generation)**: Combining search with AI generation
- **Vector Embeddings**: Mathematical representations of text
- **Semantic Search**: Finding meaning, not just keywords
- **Context Windows**: How much information AI can process at once

### Monitoring Concepts
- **Metrics**: Quantitative measurements of system performance
- **Time Series**: Data points collected over time
- **Dashboards**: Visual representations of metrics
- **Alerting**: Automated notifications of issues

### Software Architecture Concepts
- **Microservices**: Independent, deployable services
- **APIs**: Interfaces for service communication
- **Asynchronous Processing**: Non-blocking operations
- **Containerization**: Packaging applications for consistent deployment

---

## Next Steps

Now that you understand the system:

1. **Try the setup** following the step-by-step guide
2. **Explore the dashboard** and see how metrics change
3. **Ask questions** in the chat interface
4. **Experiment** with different pipeline operations
5. **Customize** the system for your needs

Remember: This is a learning platform! Don't be afraid to experiment, break things, and learn from the process. The beauty of this system is that it's designed to be understandable and modifiable.

Happy data engineering! 🚀