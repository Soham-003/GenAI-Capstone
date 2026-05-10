from .processor import DataPipelineProcessor
from ..observability.metrics import PipelineMetrics
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PipelineService:
    """Service layer for data pipeline operations"""
    
    def __init__(self):
        self.processor = DataPipelineProcessor()
        self.metrics = PipelineMetrics()
        
    def execute_pipeline(self, layer: str = "full") -> Dict[str, Any]:
        """Execute pipeline with monitoring"""
        start_time = datetime.now()
        
        try:
            self.metrics.increment_pipeline_executions(layer)
            
            if layer == "bronze-to-silver":
                result = self.processor.process_bronze_to_silver()
                self.metrics.increment_layer_transformations("bronze_to_silver")
            elif layer == "silver-to-gold":
                result = self.processor.process_silver_to_gold()
                self.metrics.increment_layer_transformations("silver_to_gold")
            else:
                result = self.processor.run_full_pipeline()
                self.metrics.increment_layer_transformations("bronze_to_silver")
                self.metrics.increment_layer_transformations("silver_to_gold")
            
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_pipeline_execution_time(execution_time, layer)
            self.metrics.update_pipeline_health(True)
            
            logger.info(f"Pipeline execution completed in {execution_time:.2f} seconds")
            
            return {
                "status": "success",
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "layer": layer
            }
            
        except Exception as e:
            self.metrics.increment_pipeline_failures(layer)
            self.metrics.update_pipeline_health(False)
            error_time = (datetime.now() - start_time).total_seconds()
            self.metrics.record_pipeline_execution_time(error_time, layer)
            
            logger.error(f"Pipeline execution failed after {error_time:.2f} seconds: {str(e)}")
            
            return {
                "status": "failed",
                "execution_time": error_time,
                "timestamp": datetime.now().isoformat(),
                "layer": layer,
                "error": str(e)
            }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline health status"""
        return {
            "last_execution": self.metrics.get_last_execution_time(),
            "total_executions": self.metrics.get_total_executions(),
            "success_rate": self.metrics.get_success_rate(),
            "avg_execution_time": self.metrics.get_avg_execution_time(),
            "recent_failures": self.metrics.get_recent_failures()
        }
    
    def validate_data_quality(self, layer: str) -> Dict[str, Any]:
        """Validate data quality for a specific layer"""
        try:
            if layer == "bronze":
                quality_report = self._validate_bronze_layer()
            elif layer == "silver":
                quality_report = self._validate_silver_layer()
            elif layer == "gold":
                quality_report = self._validate_gold_layer()
            else:
                raise ValueError(f"Unknown layer: {layer}")
            
            self.metrics.increment_quality_checks(layer)
            quality_score = self._calculate_quality_score(quality_report)
            self.metrics.set_data_quality_score(layer, quality_score)
            self.metrics.update_pipeline_health(quality_report.get("status") == "healthy")
            
            return {
                "status": "success",
                "layer": layer,
                "timestamp": datetime.now().isoformat(),
                "quality_report": quality_report,
                "quality_score": quality_score
            }
            
        except Exception as e:
            logger.error(f"Data quality validation failed for {layer}: {str(e)}")
            return {
                "status": "failed",
                "layer": layer,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def _calculate_quality_score(self, quality_report: Dict[str, Any]) -> float:
        """Translate quality report issues into a normalized score"""
        if not quality_report:
            return 0.0
        issues = quality_report.get("total_issues", len(quality_report.get("issues", [])))
        if issues == 0:
            return 100.0
        return max(0.0, 100.0 - min(issues * 25.0, 100.0))
    
    def _validate_bronze_layer(self) -> Dict[str, Any]:
        """Validate bronze layer data quality"""
        import pandas as pd
        from pathlib import Path
        
        bronze_path = Path("docs/bronze")
        issues = []
        
        # Check required files
        required_files = ["raw_customer_data.csv", "raw_transaction_data.csv", "raw_product_data.csv"]
        for file in required_files:
            if not (bronze_path / file).exists():
                issues.append(f"Missing file: {file}")
        
        # Validate data structure
        if not issues:
            try:
                customers_df = pd.read_csv(bronze_path / "raw_customer_data.csv")
                transactions_df = pd.read_csv(bronze_path / "raw_transaction_data.csv")
                products_df = pd.read_csv(bronze_path / "raw_product_data.csv")
                
                # Check for null values in critical columns
                if customers_df['customer_id'].isnull().any():
                    issues.append("Null customer_id found in customer data")
                
                if transactions_df['transaction_id'].isnull().any():
                    issues.append("Null transaction_id found in transaction data")
                
                if products_df['product_id'].isnull().any():
                    issues.append("Null product_id found in product data")
                
                # Check data consistency
                if not transactions_df['customer_id'].isin(customers_df['customer_id']).all():
                    issues.append("Transactions reference non-existent customers")
                
            except Exception as e:
                issues.append(f"Data reading error: {str(e)}")
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "status": "healthy" if len(issues) == 0 else "needs_attention"
        }
    
    def _validate_silver_layer(self) -> Dict[str, Any]:
        """Validate silver layer data quality"""
        import pandas as pd
        from pathlib import Path
        
        silver_path = Path("docs/silver")
        issues = []
        
        # Check required files
        required_files = ["processed_customers.csv", "processed_transactions.csv", "enriched_products.csv"]
        for file in required_files:
            if not (silver_path / file).exists():
                issues.append(f"Missing file: {file}")
        
        if not issues:
            try:
                customers_df = pd.read_csv(silver_path / "processed_customers.csv")
                transactions_df = pd.read_csv(silver_path / "processed_transactions.csv")
                
                # Validate transformations
                if 'email_domain' not in customers_df.columns:
                    issues.append("Missing email_domain transformation")
                
                if 'day_of_week' not in transactions_df.columns:
                    issues.append("Missing day_of_week transformation")
                
                # Check data consistency
                if not transactions_df['customer_id'].isin(customers_df['customer_id']).all():
                    issues.append("Transaction data inconsistent with customer data")
                
            except Exception as e:
                issues.append(f"Data reading error: {str(e)}")
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "status": "healthy" if len(issues) == 0 else "needs_attention"
        }
    
    def _validate_gold_layer(self) -> Dict[str, Any]:
        """Validate gold layer data quality"""
        import pandas as pd
        from pathlib import Path
        
        gold_path = Path("docs/gold")
        issues = []
        
        # Check required files
        required_files = ["customer_segmentation.csv", "monthly_performance_metrics.csv", "product_performance.csv"]
        for file in required_files:
            if not (gold_path / file).exists():
                issues.append(f"Missing file: {file}")
        
        if not issues:
            try:
                segmentation_df = pd.read_csv(gold_path / "customer_segmentation.csv")
                performance_df = pd.read_csv(gold_path / "monthly_performance_metrics.csv")
                
                # Validate aggregations
                if 'revenue_per_customer' not in segmentation_df.columns:
                    issues.append("Missing revenue_per_customer calculation")
                
                if 'success_rate' not in performance_df.columns:
                    issues.append("Missing success_rate calculation")
                
                # Check for reasonable values
                if (segmentation_df['revenue_per_customer'] < 0).any():
                    issues.append("Negative revenue_per_customer values found")
                
            except Exception as e:
                issues.append(f"Data reading error: {str(e)}")
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "status": "healthy" if len(issues) == 0 else "needs_attention"
        }
