#!/usr/bin/env python3
"""
Demo script to showcase the complete data pipeline functionality
"""

import requests
import json
import time
from typing import Dict, Any

API_BASE = "http://localhost:8000"

def print_section(title: str):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print('='*60)

def print_response(response: Dict[str, Any], title: str = ""):
    """Print API response nicely"""
    if title:
        print(f"\n📊 {title}:")
    print(json.dumps(response, indent=2, default=str))

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print("❌ API returned error:", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        print("❌ Cannot connect to API:", str(e))
        return False

def demo_pipeline_operations():
    """Demo pipeline operations"""
    print_section("Pipeline Operations Demo")
    
    # Execute full pipeline
    print("\n🔄 Executing full pipeline...")
    response = requests.post(f"{API_BASE}/pipeline/execute")
    print_response(response.json(), "Pipeline Execution Result")
    
    # Get pipeline status
    print("\n📈 Getting pipeline status...")
    response = requests.get(f"{API_BASE}/pipeline/status")
    print_response(response.json(), "Pipeline Status")
    
    # Quality checks for each layer
    for layer in ["bronze", "silver", "gold"]:
        print(f"\n🔍 Running quality check for {layer} layer...")
        response = requests.post(f"{API_BASE}/pipeline/quality-check", params={"layer": layer})
        print_response(response.json(), f"{layer.title()} Layer Quality Check")

def demo_catalogue_exploration():
    """Demo data catalogue exploration"""
    print_section("Data Catalogue Demo")
    
    # Scan data layers
    print("\n🔍 Scanning data layers...")
    response = requests.post(f"{API_BASE}/catalogue/scan")
    print_response(response.json(), "Catalogue Scan Result")
    
    # List all tables
    print("\n📋 Listing all tables...")
    response = requests.get(f"{API_BASE}/catalogue/tables")
    tables = response.json()
    print_response(tables, "All Tables")
    
    # Get specific table info
    if tables.get("tables"):
        first_table_key = list(tables["tables"].keys())[0]
        print(f"\n📄 Getting details for {first_table_key}...")
        response = requests.get(f"{API_BASE}/catalogue/tables/{first_table_key}")
        print_response(response.json(), "Table Details")
    
    # Search tables
    print("\n🔎 Searching for 'customer' tables...")
    response = requests.get(f"{API_BASE}/catalogue/search", params={"query": "customer"})
    print_response(response.json(), "Search Results")
    
    # Get lineage diagram
    print("\n🌐 Getting data lineage...")
    response = requests.get(f"{API_BASE}/catalogue/lineage")
    print_response(response.json(), "Data Lineage")
    
    # Get PII summary
    print("\n🔒 Getting PII summary...")
    response = requests.get(f"{API_BASE}/catalogue/pii")
    print_response(response.json(), "PII Summary")

def demo_agentic_actions():
    """Demo agentic quality actions"""
    print_section("Agentic Actions Demo")
    
    # Run comprehensive quality check
    print("\n🎯 Running comprehensive quality check...")
    response = requests.post(f"{API_BASE}/agents/quality/comprehensive")
    print_response(response.json(), "Comprehensive Quality Check")
    
    # Get quality status
    print("\n📊 Getting current quality status...")
    response = requests.get(f"{API_BASE}/agents/quality/status")
    print_response(response.json(), "Quality Status")
    
    # Trigger specific quality action
    print("\n⚡ Triggering pipeline validation...")
    response = requests.post(f"{API_BASE}/agents/quality/trigger", 
                           params={"action_type": "pipeline_validation"})
    print_response(response.json(), "Pipeline Validation")

def demo_real_time_monitoring():
    """Demo real-time monitoring"""
    print_section("Real-time Monitoring Demo")
    
    print("\n📈 Simulating real-time pipeline operations...")
    
    for i in range(3):
        print(f"\n--- Iteration {i+1} ---")
        
        # Execute pipeline
        response = requests.post(f"{API_BASE}/pipeline/execute")
        result = response.json()
        print(f"Pipeline execution: {result['status']} ({result['execution_time']:.2f}s)")
        
        # Get status
        response = requests.get(f"{API_BASE}/pipeline/status")
        status = response.json()
        print(f"Success rate: {status['success_rate']:.1f}%")
        print(f"Total executions: {status['total_executions']}")
        
        # Small delay to simulate real-time
        time.sleep(2)

def main():
    """Main demo function"""
    print("🎯 Data Pipeline Demo Starting...")
    print("Make sure the API is running on http://localhost:8000")
    print("Start with: uvicorn app.api.main:app --reload --port 8000")
    
    # Check API health
    if not check_api_health():
        print("\n❌ Please start the API server first!")
        return
    
    try:
        # Run all demos
        demo_pipeline_operations()
        demo_catalogue_exploration()
        demo_agentic_actions()
        demo_real_time_monitoring()
        
        print_section("Demo Complete! 🎉")
        print("\n📊 Check out the Grafana dashboard at: http://localhost:3000")
        print("🔍 Explore the API documentation at: http://localhost:8000/docs")
        print("💬 Try the Streamlit chat interface: streamlit run app/ui/streamlit_app.py")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")

if __name__ == "__main__":
    main()
