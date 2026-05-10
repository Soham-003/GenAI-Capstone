import logging
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from datetime import datetime, timedelta
from typing import Dict, List

from app.config import settings

logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter("assistant_requests_total", "Total assistant requests")
QUALITY_ACTION_COUNT = Counter("assistant_quality_checks_total", "Total quality-check actions")
LATENCY_SECONDS = Histogram("assistant_request_latency_seconds", "Assistant response latency")

# Pipeline metrics
PIPELINE_EXECUTIONS = Counter("pipeline_executions_total", "Total pipeline executions", ["layer"])
PIPELINE_FAILURES = Counter("pipeline_failures_total", "Total pipeline failures", ["layer"])
PIPELINE_EXECUTION_TIME = Histogram("pipeline_execution_time_seconds", "Pipeline execution time", ["layer"])
LAYER_TRANSFORMATIONS = Counter("layer_transformations_total", "Total layer transformations", ["transformation"])
QUALITY_CHECKS = Counter("quality_checks_total", "Total quality checks", ["layer"])
DATA_QUALITY_SCORE = Gauge("data_quality_score", "Data quality score", ["layer"])
CATALOGUE_TABLES_COUNT = Gauge("catalogue_tables_count", "Number of tables discovered in data catalogue")
CATALOGUE_PII_TABLE_COUNT = Gauge("catalogue_pii_table_count", "Number of PII-tagged tables in the catalogue")
CATALOGUE_LINEAGE_RELATIONS_COUNT = Gauge("catalogue_lineage_relations_count", "Number of lineage relationships in the catalogue")
PIPELINE_HEALTH = Gauge("pipeline_health_status", "Pipeline health status (1=healthy, 0=unhealthy)")
LAST_EXECUTION_TIME = Gauge("pipeline_last_execution_timestamp", "Timestamp of last pipeline execution")

_started = False


def start_metrics_server() -> None:
    global _started
    if not _started:
        try:
            start_http_server(settings.prometheus_port)
            _started = True
            logger.info(f"✓ Prometheus metrics server started on port {settings.prometheus_port}")
        except OSError as e:
            logger.error(
                f"✗ Failed to start metrics server on port {settings.prometheus_port}: {e}. "
                f"Metrics will not be exposed. Ensure port {settings.prometheus_port} is available "
                f"and Prometheus is configured to scrape http://host.docker.internal:{settings.prometheus_port}/metrics"
            )
            raise


def get_metrics_status() -> dict[str, bool]:
    """Check if metrics server is running and metrics are being exported."""
    return {
        "metrics_server_initialized": _started,
        "request_count": float(REQUEST_COUNT._value.get()),
        "quality_checks_count": float(QUALITY_ACTION_COUNT._value.get()),
    }


class PipelineMetrics:
    """Pipeline-specific metrics tracking"""
    
    def __init__(self):
        self._execution_history: List[Dict] = []
        self._failure_history: List[Dict] = []
        self._quality_check_history: List[Dict] = []
        
    def increment_pipeline_executions(self, layer: str = "full"):
        """Increment pipeline execution counter"""
        PIPELINE_EXECUTIONS.labels(layer=layer).inc()
        LAST_EXECUTION_TIME.set(datetime.now().timestamp())
        
    def increment_pipeline_failures(self, layer: str = "full"):
        """Increment pipeline failure counter"""
        PIPELINE_FAILURES.labels(layer=layer).inc()
        self._failure_history.append({
            "timestamp": datetime.now().isoformat(),
            "layer": layer
        })
        
    def record_pipeline_execution_time(self, duration: float, layer: str = "full"):
        """Record pipeline execution time"""
        PIPELINE_EXECUTION_TIME.labels(layer=layer).observe(duration)
        self._execution_history.append({
            "timestamp": datetime.now().isoformat(),
            "duration": duration,
            "layer": layer
        })
        
    def increment_layer_transformations(self, transformation: str):
        """Increment layer transformation counter"""
        LAYER_TRANSFORMATIONS.labels(transformation=transformation).inc()
        
    def increment_quality_checks(self, layer: str):
        """Increment quality check counter"""
        QUALITY_CHECKS.labels(layer=layer).inc()
        self._quality_check_history.append({
            "timestamp": datetime.now().isoformat(),
            "layer": layer
        })
        
    def set_data_quality_score(self, layer: str, score: float):
        """Set data quality score for a layer"""
        DATA_QUALITY_SCORE.labels(layer=layer).set(score)
        
    def set_catalogue_insights(self, tables_count: int, pii_table_count: int, lineage_relations_count: int):
        """Set catalogue summary metrics for Grafana"""
        CATALOGUE_TABLES_COUNT.set(tables_count)
        CATALOGUE_PII_TABLE_COUNT.set(pii_table_count)
        CATALOGUE_LINEAGE_RELATIONS_COUNT.set(lineage_relations_count)
        
    def update_pipeline_health(self, is_healthy: bool):
        """Update overall pipeline health status"""
        PIPELINE_HEALTH.set(1 if is_healthy else 0)
        
    def get_last_execution_time(self) -> str:
        """Get timestamp of last execution"""
        if self._execution_history:
            return self._execution_history[-1]["timestamp"]
        return None
        
    def get_total_executions(self) -> int:
        """Get total number of executions"""
        return len(self._execution_history)
        
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        total_executions = len(self._execution_history)
        total_failures = len(self._failure_history)
        if total_executions == 0:
            return 0.0
        return ((total_executions - total_failures) / total_executions) * 100
        
    def get_avg_execution_time(self) -> float:
        """Get average execution time in seconds"""
        if not self._execution_history:
            return 0.0
        return sum(exec["duration"] for exec in self._execution_history) / len(self._execution_history)
        
    def get_recent_failures(self, hours: int = 24) -> List[Dict]:
        """Get failures from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            failure for failure in self._failure_history
            if datetime.fromisoformat(failure["timestamp"]) > cutoff_time
        ]
