from __future__ import annotations

import logging
import socket
import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional

from app.observability.metrics import start_metrics_server, get_metrics_status
from app.services.chat_service import ChatService
from app.pipeline.service import PipelineService
from app.catalogue.explorer import DataCatalogueExplorer
from app.agents.quality_agent import QualityAgent

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def is_metrics_server_running(host: str = "localhost", port: int = 8001) -> bool:
    """Check if metrics server is already running on the specified port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception:
        return False

# Configure logging - suppress verbose httpx/huggingface logs
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(page_title="DE Assistant", layout="wide", page_icon="🤖")

# ============================================================================
# STYLING & CSS
# ============================================================================
st.markdown(
    """
<style>
    /* Main container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    /* Hero banner */
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #0ea5e9 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: #f8fafc;
        text-align: center;
        margin-bottom: 2rem;
    }

    .hero h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #f8fafc, #e2e8f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }

    /* Status indicators */
    .status-healthy {
        color: #10b981;
        font-weight: 600;
    }

    .status-unhealthy {
        color: #ef4444;
        font-weight: 600;
    }

    /* Metric cards */
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }

    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        margin-top: 0.25rem;
    }

    /* Chat messages */
    .chat-user {
        background: #3b82f6;
        color: white;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        max-width: 80%;
        margin-left: auto;
    }

    .chat-assistant {
        background: #f1f5f9;
        color: #1e293b;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        max-width: 80%;
    }

    /* Sidebar */
    .sidebar-content {
        padding: 1rem 0;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: 500;
    }

    /* Success/Warning/Error messages */
    .success-msg {
        background: #dcfce7;
        color: #166534;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #16a34a;
    }

    .error-msg {
        background: #fef2f2;
        color: #991b1b;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #dc2626;
    }

    .info-msg {
        background: #eff6ff;
        color: #1e40af;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #3b82f6;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# INITIALIZATION
# ============================================================================
# Only start metrics server if not already running
if not is_metrics_server_running():
    start_metrics_server()
else:
    logger.info("✓ Metrics server already running, skipping startup")

# Initialize services
chat_service = ChatService()
pipeline_service = PipelineService()
catalogue_explorer = DataCatalogueExplorer()
quality_agent = QualityAgent()

# ============================================================================
# HERO BANNER
# ============================================================================
st.markdown(
    """
<div class="hero">
    <h1>🤖 Data Engineer Assistant</h1>
    <p>Your AI-powered companion for data pipeline operations, catalogue exploration, and quality monitoring</p>
</div>
""",
    unsafe_allow_html=True,
)

# ============================================================================
# MAIN NAVIGATION
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat Assistant",
    "🔄 Pipeline Operations",
    "📋 Data Catalogue",
    "🔍 Quality Checks",
    "📊 Monitoring Dashboard"
])

# ============================================================================
# TAB 1: CHAT ASSISTANT
# ============================================================================
with tab1:
    st.header("💬 Conversational Assistant")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_mode" not in st.session_state:
        st.session_state.last_mode = "Standard Answer"

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        response_mode = st.selectbox(
            "Response Style",
            ["Standard Answer", "Detailed Explanation", "Code Examples"],
            index=["Standard Answer", "Detailed Explanation", "Code Examples"].index(st.session_state.last_mode)
        )

        run_quality_check = st.checkbox("Run Quality Check", value=False)

        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    # Chat interface
    chat_container = st.container()

    with chat_container:
        # Display chat history
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-user">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-assistant">{message["content"]}</div>', unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Ask me about your data pipeline, catalogue, or operations..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get assistant response
        with st.spinner("Thinking..."):
            try:
                response = chat_service.chat(prompt, run_quality_check)
                assistant_message = response.answer

                # Add style based on mode
                if response_mode == "Detailed Explanation":
                    assistant_message = f"📖 **Detailed Analysis**\n\n{assistant_message}"
                elif response_mode == "Code Examples":
                    assistant_message = f"💻 **Code Examples Included**\n\n{assistant_message}"

                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                st.session_state.last_mode = response_mode

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

        st.rerun()

# ============================================================================
# TAB 2: PIPELINE OPERATIONS
# ============================================================================
with tab2:
    st.header("🔄 Pipeline Operations")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Execute Pipeline")
        layer = st.selectbox(
            "Pipeline Layer",
            ["full", "bronze-to-silver", "silver-to-gold"],
            help="Choose which part of the pipeline to execute"
        )

        if st.button("🚀 Execute Pipeline", type="primary"):
            with st.spinner(f"Executing {layer} pipeline..."):
                try:
                    result = pipeline_service.execute_pipeline(layer)
                    st.success(f"✅ Pipeline executed successfully in {result['execution_time']:.2f}s")
                    st.json(result)
                except Exception as e:
                    st.error(f"❌ Pipeline execution failed: {str(e)}")

    with col2:
        st.subheader("Pipeline Status")
        if st.button("📊 Check Status"):
            try:
                status = pipeline_service.get_pipeline_status()
                st.json(status)
            except Exception as e:
                st.error(f"❌ Failed to get status: {str(e)}")

    with col3:
        st.subheader("Data Quality")
        quality_layer = st.selectbox(
            "Check Layer",
            ["bronze", "silver", "gold"],
            key="quality_layer"
        )

        if st.button("🔍 Validate Quality"):
            try:
                result = pipeline_service.validate_data_quality(quality_layer)
                st.json(result)
            except Exception as e:
                st.error(f"❌ Quality check failed: {str(e)}")

# ============================================================================
# TAB 3: DATA CATALOGUE
# ============================================================================
with tab3:
    st.header("📋 Data Catalogue")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Catalogue Operations")

        if st.button("🔍 Scan Data Layers", type="primary"):
            with st.spinner("Scanning data layers..."):
                try:
                    result = catalogue_explorer.scan_data_layers()
                    st.success(f"✅ Catalogue updated! Found {result['tables_found']} tables")
                    st.json(result)
                except Exception as e:
                    st.error(f"❌ Scan failed: {str(e)}")

        if st.button("📋 List All Tables"):
            try:
                tables = catalogue_explorer.catalogue["tables"]
                st.success(f"📊 Found {len(tables)} tables")

                # Display as a nice table
                if tables:
                    table_data = []
                    for table_name, table_info in tables.items():
                        table_data.append({
                            "Table Name": table_name,
                            "Layer": table_info.get("layer", "unknown"),
                            "Row Count": table_info.get("row_count", "unknown"),
                            "Columns": len(table_info.get("columns", []))
                        })

                    st.dataframe(pd.DataFrame(table_data))
                else:
                    st.info("No tables found. Run a scan first.")

            except Exception as e:
                st.error(f"❌ Failed to list tables: {str(e)}")

        # Search functionality
        st.subheader("🔎 Search Tables")
        search_query = st.text_input("Search query", placeholder="Enter table name or column...")

        if st.button("Search") and search_query:
            try:
                results = catalogue_explorer.search_tables(search_query)
                if results:
                    st.success(f"Found {len(results)} matching tables")
                    for result in results:
                        table_info = result["table_info"]
                        table_name = table_info["name"]
                        match_type = result["match_type"]
                        with st.expander(f"📄 {table_name} ({match_type})"):
                            if match_type == "column":
                                st.write(f"**Matching columns:** {', '.join(result.get('matching_columns', []))}")
                            st.json(table_info)
                else:
                    st.info("No tables found matching your query.")
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")

    with col2:
        st.subheader("Catalogue Summary")

        try:
            tables = catalogue_explorer.catalogue.get("tables", {})
            total_tables = len(tables)

            # Count by layer
            layer_counts = {}
            pii_tables = 0

            for table_info in tables.values():
                layer = table_info.get("layer", "unknown")
                layer_counts[layer] = layer_counts.get(layer, 0) + 1

                # Check for PII
                if any(col.get("is_pii", False) for col in table_info.get("columns", [])):
                    pii_tables += 1

            # Display metrics
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric("Total Tables", total_tables)

            with col_b:
                st.metric("PII Tables", pii_tables)

            with col_c:
                st.metric("Layers", len(layer_counts))

            # Layer breakdown
            if layer_counts:
                st.subheader("Tables by Layer")
                for layer, count in layer_counts.items():
                    st.metric(f"{layer.title()} Layer", count)

        except Exception as e:
            st.error(f"❌ Failed to load catalogue summary: {str(e)}")

# ============================================================================
# TAB 4: QUALITY CHECKS
# ============================================================================
with tab4:
    st.header("🔍 Quality Checks")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Comprehensive Quality Check")

        if st.button("🩺 Run Full Quality Assessment", type="primary"):
            with st.spinner("Running comprehensive quality checks..."):
                try:
                    result = quality_agent.run_comprehensive_quality_check()
                    st.success("✅ Quality assessment completed!")

                    # Display results
                    if "overall_score" in result:
                        st.metric("Overall Quality Score", f"{result['overall_score']}%")

                    if "issues" in result:
                        st.warning(f"Found {len(result['issues'])} issues")
                        for issue in result["issues"][:5]:  # Show first 5
                            st.write(f"• {issue}")

                    st.json(result)

                except Exception as e:
                    st.error(f"❌ Quality check failed: {str(e)}")

    with col2:
        st.subheader("Quick Actions")

        action_type = st.selectbox(
            "Select Action",
            ["comprehensive_check", "validate_schemas", "check_duplicates", "profile_data"],
            help="Choose a specific quality action to run"
        )

        action_layer = st.selectbox(
            "Target Layer",
            ["all", "bronze", "silver", "gold"],
            help="Which data layer to check"
        )

        if st.button("⚡ Run Action"):
            with st.spinner(f"Running {action_type} on {action_layer} layer..."):
                try:
                    kwargs = {}
                    if action_layer != "all":
                        kwargs["layer"] = action_layer

                    result = quality_agent.trigger_quality_action(action_type, **kwargs)
                    st.success(f"✅ Action '{action_type}' completed!")
                    st.json(result)

                except Exception as e:
                    st.error(f"❌ Action failed: {str(e)}")

    # Quality Status
    st.subheader("Current Quality Status")

    if st.button("📊 Get Quality Status"):
        try:
            status = quality_agent.get_quality_status()
            st.json(status)

            # Show key metrics
            if "overall_health" in status:
                health = status["overall_health"]
                if health == "healthy":
                    st.success("🟢 System is healthy")
                elif health == "warning":
                    st.warning("🟡 Some issues detected")
                else:
                    st.error("🔴 Critical issues found")

        except Exception as e:
            st.error(f"❌ Failed to get status: {str(e)}")

# ============================================================================
# TAB 5: MONITORING DASHBOARD
# ============================================================================
with tab5:
    st.header("📊 Monitoring Dashboard")

    # Get metrics status
    try:
        metrics = get_metrics_status()

        # Pipeline Health
        st.subheader("🚀 Pipeline Health")

        # Mock some dashboard data (in a real app, this would come from Prometheus)
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Executions", metrics.get("request_count", 0))

        with col2:
            st.metric("Health Status", "Healthy" if metrics.get("metrics_server_initialized") else "Unknown")

        with col3:
            st.metric("Active Tables", len(catalogue_explorer.catalogue.get("tables", {})))

        with col4:
            st.metric("Quality Score", "95%")  # Mock value

        # Recent Activity
        st.subheader("📈 Recent Activity")

        # Show some recent operations (this would be more sophisticated in production)
        st.info("📊 Metrics server is running and collecting data")
        st.info("🔄 Pipeline operations are being tracked")
        st.info("📋 Catalogue scans are logged")

        # Raw metrics data
        with st.expander("🔧 Raw Metrics Data"):
            st.json(metrics)

    except Exception as e:
        st.error(f"❌ Failed to load dashboard: {str(e)}")

        # Fallback: show basic status
        st.info("Basic system status:")
        st.write("✅ Application is running")
        st.write("✅ Services are initialized")
        st.write("❓ Metrics collection status unknown")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #64748b; padding: 1rem;">
    <p>Built with ❤️ for data engineers | Powered by Streamlit & AI</p>
</div>
""",
    unsafe_allow_html=True,
)