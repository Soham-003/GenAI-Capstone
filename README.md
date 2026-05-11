# Data Engineer Assistant

AI-powered data pipeline management system with conversational interface for data engineering operations.

## 🎯 Overview

This project provides a comprehensive solution for data pipeline management, combining conversational AI with automated data processing, quality monitoring, and real-time dashboards. Built for data engineers who need efficient pipeline operations with intelligent assistance.

## ✨ Key Features

### 🤖 Conversational Assistant
- **Project-Specific Q&A**: Ask questions about your pipeline architecture, datasets, and operations
- **Intelligent Responses**: RAG-powered answers using your actual project documentation
- **Codebase Understanding**: Get insights about design decisions and implementation details
- **Natural Language Interface**: Chat-based interaction with streaming responses

### 🔄 Pipeline Operations
- **Bronze-Silver-Gold Architecture**: Complete medallion data pipeline implementation
- **One-Click Execution**: Execute full pipeline or individual layer transformations
- **Data Quality Validation**: Built-in quality checks and validation
- **Real-time Processing**: Automatic detection and processing of new data files

### 📋 Data Catalogue
- **Automatic Discovery**: Scan and index all data tables across layers
- **Metadata Management**: Track schemas, PII tags, and data lineage
- **Search Functionality**: Find tables by name, column, or content
- **PII Detection**: Automatic identification and tagging of sensitive data

### 🔍 Quality Monitoring
- **Automated Quality Checks**: Comprehensive data validation across all layers
- **Quality Metrics**: Completeness, uniqueness, validity scoring
- **Agentic Actions**: On-demand quality assessments and recommendations
- **Real-time Alerts**: Automated notifications for quality issues

### 📊 Monitoring Dashboard
- **Real-time Metrics**: Live system performance and pipeline health
- **Visual Analytics**: Grafana dashboards with key performance indicators
- **Health Status**: System monitoring with SLO adherence tracking
- **Historical Trends**: Performance analysis and capacity planning

## 🏗️ Technical Architecture

### Core Components
- **Frontend**: Streamlit web application with responsive design
- **AI Backend**: OpenAI integration with intelligent prompting
- **Vector Database**: ChromaDB for semantic search and retrieval
- **Data Processing**: Python-based pipeline with pandas transformations
- **Monitoring**: Prometheus metrics collection and Grafana visualization

### Data Flow
1. **Ingestion**: Raw data enters bronze layer
2. **Processing**: Automated transformations to silver layer
3. **Aggregation**: Business insights in gold layer
4. **Quality**: Continuous validation at each stage
5. **Monitoring**: Real-time metrics and alerts

## 🚀 Quick Start

### Prerequisites
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

### Setup and Launch
```bash
# 1. Build knowledge base with project documentation
python -m app.rag.ingestion

# 2. Start the application
streamlit run app/ui/streamlit_app.py

# 3. Access the application
# Web Interface: http://localhost:8501
# API Documentation: http://localhost:8000/docs
```

### Optional Monitoring Setup
```bash
# Start monitoring stack
docker-compose up -d

# Access dashboards
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

## 📁 Project Structure

```
GenAI Capstone/
├── app/                          # Core application
│   ├── rag/                     # RAG indexing and retrieval
│   │   ├── ingestion.py         # Document processing and chunking
│   │   └── retriever.py         # Semantic search functionality
│   ├── services/                 # Business logic layer
│   │   └── chat_service.py      # AI conversation orchestration
│   ├── pipeline/                  # Data processing engine
│   │   ├── processor.py         # Bronze-Silver-Gold transformations
│   │   └── service.py          # Pipeline orchestration
│   ├── catalogue/                 # Data discovery and metadata
│   │   └── explorer.py          # Table scanning and search
│   ├── agents/                    # Quality automation
│   │   ├── quality_agent.py     # Quality checks and assessments
│   │   └── actions.py           # Agentic quality operations
│   ├── observability/             # Metrics and monitoring
│   │   └── metrics.py          # Prometheus integration
│   └── ui/
│       └── streamlit_app.py     # Main web interface
├── docs/                         # Data layers
│   ├── bronze/                  # Raw data files
│   ├── silver/                  # Processed data files
│   └── gold/                    # Aggregated insights
├── infra/                        # Infrastructure components
│   ├── grafana/                 # Dashboard configurations
│   ├── prometheus/              # Metrics setup
│   └── docker-compose.yml        # Container orchestration
├── slides/                       # Documentation and presentations
│   └── deck.md                # Project overview deck
└── README.md                     # This file
```

## 🔄 Data Pipeline Architecture

### Bronze Layer (Raw Data)
- **Purpose**: Ingestion of raw, unprocessed data from source systems
- **Characteristics**: 
  - Raw format from source systems
  - May contain quality issues and duplicates
  - Potential PII data requiring special handling
  - No validation or cleaning applied
- **Processing**: Automatic file detection and ingestion
- **Output**: Cleaned data ready for silver layer

### Silver Layer (Processed Data)
- **Purpose**: Data cleaning, validation, and enrichment
- **Transformations**:
  - **Customer Data**: Email domain extraction, age grouping, income tiering
  - **Transaction Data**: Date parsing, temporal analysis, validation
  - **Product Data**: Price categorization, stock status determination
- **Quality Improvements**: Missing value handling, duplicate removal, consistency checks

### Gold Layer (Business Insights)
- **Purpose**: Aggregated business metrics and KPIs for decision making
- **Aggregations**:
  - **Customer Segmentation**: Value-based and behavioral grouping
  - **Performance Metrics**: Monthly revenue, transaction trends
  - **Product Analytics**: Category performance and insights
- **Output**: Business-ready data for reporting and analytics

## 🎯 Usage Examples

### Conversational Assistant
```python
# Ask about pipeline architecture
"What transformations are applied to customer data?"

# Get dataset information
"List me few rows of datasets we used"

# Understand data quality
"What quality checks are performed on silver layer?"
```

### Pipeline Operations
```python
# Execute full pipeline
pipeline_service.execute_pipeline("full")

# Execute specific layer
pipeline_service.execute_pipeline("bronze-to-silver")

# Check pipeline health
pipeline_service.get_pipeline_status()
```

### Data Catalogue
```python
# Discover all tables
catalogue_explorer.scan_data_layers()

# Search for specific tables
catalogue_explorer.search_tables("customer")

# Get PII information
catalogue_explorer.get_pii_summary()
```

## 🔧 Configuration

### Environment Variables
Create `.env` file with:
```bash
OPENAI_API_KEY=your_openai_api_key_here
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Customization
- **Data Paths**: Modify `docs/` folder structure for your data
- **Pipeline Logic**: Update transformation rules in `app/pipeline/processor.py`
- **Quality Rules**: Customize validation criteria in `app/agents/quality_agent.py`
- **UI Themes**: Modify Streamlit styling in `app/ui/streamlit_app.py`

## 🧪 Testing

```bash
# Run all tests
pytest -v

# Run specific test modules
pytest tests/test_pipeline.py
pytest tests/test_catalogue.py
```

## 📚 Documentation

- **API Documentation**: Available at `http://localhost:8000/docs`
- **Code Comments**: Comprehensive inline documentation throughout codebase
- **Presentation Deck**: `slides/deck.md` for stakeholder overview
- **Architecture Details**: Detailed implementation notes in code files

## 🚀 Deployment

### Development
```bash
# Local development
streamlit run app/ui/streamlit_app.py

# With monitoring
docker-compose up -d
```

### Production Considerations
- **Scalability**: Bronze-Silver-Gold architecture supports horizontal scaling
- **Monitoring**: Real-time metrics for production observability
- **Security**: PII detection and masking for compliance
- **Reliability**: Error handling and recovery mechanisms

---

## 📞 Support

For issues, questions, or contributions:
- **Documentation**: Refer to inline code comments and API docs
- **Issues**: Check existing GitHub issues or create new ones
- **Features**: Request enhancements through GitHub issues

---

**MIT License** - See LICENSE file for details

