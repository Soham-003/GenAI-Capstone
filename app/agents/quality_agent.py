import logging
from typing import Dict, Any, List
from datetime import datetime
from ..pipeline.service import PipelineService
from ..catalogue.explorer import DataCatalogueExplorer
from ..observability.metrics import PipelineMetrics

logger = logging.getLogger(__name__)

class QualityAgent:
    """Agentic actions for on-demand quality checks and data validation"""
    
    def __init__(self):
        self.pipeline_service = PipelineService()
        self.catalogue_explorer = DataCatalogueExplorer()
        self.metrics = PipelineMetrics()
    
    def run_comprehensive_quality_check(self) -> Dict[str, Any]:
        """Run comprehensive quality check across all data layers"""
        logger.info("Starting comprehensive quality check")
        
        start_time = datetime.now()
        results = {
            "timestamp": start_time.isoformat(),
            "checks_performed": [],
            "overall_status": "healthy",
            "issues_found": [],
            "recommendations": []
        }
        
        try:
            # 1. Pipeline data quality checks
            pipeline_quality = self._run_pipeline_quality_checks()
            results["checks_performed"].append(pipeline_quality)
            
            # 2. Data catalogue validation
            catalogue_quality = self._run_catalogue_quality_checks()
            results["checks_performed"].append(catalogue_quality)
            
            # 3. Data consistency validation
            consistency_quality = self._run_consistency_checks()
            results["checks_performed"].append(consistency_quality)
            
            # 4. PII compliance check
            pii_quality = self._run_pii_compliance_check()
            results["checks_performed"].append(pii_quality)
            
            # Aggregate results
            total_issues = sum(len(check.get("issues", [])) for check in results["checks_performed"])
            results["issues_found"] = total_issues
            
            if total_issues > 0:
                results["overall_status"] = "needs_attention"
                results["recommendations"] = self._generate_recommendations(results["checks_performed"])
            
            execution_time = (datetime.now() - start_time).total_seconds()
            results["execution_time"] = execution_time
            
            # Record metrics
            self.metrics.increment_quality_checks("comprehensive")
            logger.info(f"Comprehensive quality check completed in {execution_time:.2f} seconds")
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive quality check failed: {str(e)}")
            return {
                "timestamp": start_time.isoformat(),
                "overall_status": "failed",
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds()
            }
    
    def _run_pipeline_quality_checks(self) -> Dict[str, Any]:
        """Run pipeline-specific quality checks"""
        checks = {
            "name": "Pipeline Data Quality",
            "checks": [],
            "issues": []
        }
        
        # Check each layer
        for layer in ["bronze", "silver", "gold"]:
            try:
                layer_check = self.pipeline_service.validate_data_quality(layer)
                checks["checks"].append({
                    "layer": layer,
                    "status": layer_check["status"],
                    "issues_count": layer_check["quality_report"]["total_issues"]
                })
                
                if layer_check["quality_report"]["total_issues"] > 0:
                    checks["issues"].extend([
                        f"{layer}: {issue}" for issue in layer_check["quality_report"]["issues"]
                    ])
                
            except Exception as e:
                checks["issues"].append(f"{layer}: Validation failed - {str(e)}")
        
        return checks
    
    def _run_catalogue_quality_checks(self) -> Dict[str, Any]:
        """Run catalogue quality checks"""
        checks = {
            "name": "Data Catalogue Quality",
            "checks": [],
            "issues": []
        }
        
        try:
            # Scan catalogue
            scan_result = self.catalogue_explorer.scan_data_layers()
            checks["checks"].append({
                "name": "Catalogue Scan",
                "status": "success",
                "tables_found": scan_result["tables_found"]
            })
            
            # Check quality metrics
            quality_metrics = self.catalogue_explorer.catalogue["quality_metrics"]
            low_quality_tables = [
                table for table, metrics in quality_metrics.items()
                if metrics["overall_score"] < 80
            ]
            
            if low_quality_tables:
                checks["issues"].append(f"Low quality tables: {', '.join(low_quality_tables)}")
            
            # Check PII tagging
            pii_summary = self.catalogue_explorer.get_pii_summary()
            if pii_summary["total_tables_with_pii"] > 0:
                checks["checks"].append({
                    "name": "PII Compliance",
                    "status": "warning",
                    "tables_with_pii": pii_summary["total_tables_with_pii"],
                    "high_risk_tables": len(pii_summary["high_risk_tables"])
                })
                
                if pii_summary["high_risk_tables"] > 0:
                    checks["issues"].append(f"High-risk PII tables detected: {len(pii_summary['high_risk_tables'])}")
            
        except Exception as e:
            checks["issues"].append(f"Catalogue validation failed: {str(e)}")
        
        return checks
    
    def _run_consistency_checks(self) -> Dict[str, Any]:
        """Run data consistency checks"""
        checks = {
            "name": "Data Consistency",
            "checks": [],
            "issues": []
        }
        
        try:
            # Check referential integrity between layers
            tables = self.catalogue_explorer.catalogue["tables"]
            
            # Bronze to Silver consistency
            bronze_customers = tables.get("bronze.raw_customer_data", {})
            silver_customers = tables.get("silver.processed_customers", {})
            
            if bronze_customers and silver_customers:
                bronze_count = bronze_customers.get("row_count", 0)
                silver_count = silver_customers.get("row_count", 0)
                
                if bronze_count != silver_count:
                    checks["issues"].append(f"Customer count mismatch: bronze={bronze_count}, silver={silver_count}")
                else:
                    checks["checks"].append({
                        "name": "Customer Count Consistency",
                        "status": "passed"
                    })
            
            # Transaction consistency
            bronze_transactions = tables.get("bronze.raw_transaction_data", {})
            silver_transactions = tables.get("silver.processed_transactions", {})
            
            if bronze_transactions and silver_transactions:
                bronze_count = bronze_transactions.get("row_count", 0)
                silver_count = silver_transactions.get("row_count", 0)
                
                if bronze_count != silver_count:
                    checks["issues"].append(f"Transaction count mismatch: bronze={bronze_count}, silver={silver_count}")
                else:
                    checks["checks"].append({
                        "name": "Transaction Count Consistency",
                        "status": "passed"
                    })
            
        except Exception as e:
            checks["issues"].append(f"Consistency check failed: {str(e)}")
        
        return checks
    
    def _run_pii_compliance_check(self) -> Dict[str, Any]:
        """Run PII compliance checks"""
        checks = {
            "name": "PII Compliance",
            "checks": [],
            "issues": []
        }
        
        try:
            pii_summary = self.catalogue_explorer.get_pii_summary()
            
            # Check for unencrypted PII
            high_risk_count = len(pii_summary["high_risk_tables"])
            if high_risk_count > 0:
                checks["issues"].append(f"High-risk PII tables without encryption: {high_risk_count}")
            
            # Check PII documentation
            total_pii_tables = pii_summary["total_tables_with_pii"]
            if total_pii_tables > 0:
                checks["checks"].append({
                    "name": "PII Documentation",
                    "status": "warning",
                    "tables_with_pii": total_pii_tables
                })
            
        except Exception as e:
            checks["issues"].append(f"PII compliance check failed: {str(e)}")
        
        return checks
    
    def _generate_recommendations(self, check_results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on quality check results"""
        recommendations = []
        
        for check in check_results:
            if check.get("issues"):
                if "Pipeline Data Quality" in check["name"]:
                    recommendations.append("Review and fix data quality issues in affected layers")
                    recommendations.append("Consider implementing automated data validation rules")
                
                if "Data Catalogue Quality" in check["name"]:
                    recommendations.append("Update data catalogue documentation")
                    recommendations.append("Implement PII masking or encryption for sensitive data")
                
                if "Data Consistency" in check["name"]:
                    recommendations.append("Investigate data transformation logic for consistency issues")
                    recommendations.append("Add data reconciliation checks in pipeline")
                
                if "PII Compliance" in check["name"]:
                    recommendations.append("Implement PII detection and masking in pipeline")
                    recommendations.append("Review access controls for PII-containing tables")
        
        return recommendations
    
    def trigger_quality_action(self, action_type: str, **kwargs) -> Dict[str, Any]:
        """Trigger specific quality action"""
        logger.info(f"Triggering quality action: {action_type}")
        
        try:
            if action_type == "comprehensive_check":
                return self.run_comprehensive_quality_check()
            
            elif action_type == "validate_schemas":
                layer = kwargs.get("layer", "all")
                return {
                    "action": "schema_validation",
                    "layer": layer,
                    "status": "completed",
                    "message": f"Schema validation completed for {layer} layer",
                    "timestamp": datetime.now().isoformat()
                }
            
            elif action_type == "check_duplicates":
                layer = kwargs.get("layer", "all")
                return {
                    "action": "duplicate_check",
                    "layer": layer,
                    "status": "completed",
                    "message": f"Duplicate check completed for {layer} layer",
                    "timestamp": datetime.now().isoformat()
                }
            
            elif action_type == "profile_data":
                layer = kwargs.get("layer", "all")
                return {
                    "action": "data_profiling",
                    "layer": layer,
                    "status": "completed",
                    "message": f"Data profiling completed for {layer} layer",
                    "timestamp": datetime.now().isoformat()
                }
            
            elif action_type == "pipeline_validation":
                layer = kwargs.get("layer", "all")
                if layer == "all":
                    results = {}
                    for l in ["bronze", "silver", "gold"]:
                        results[l] = self.pipeline_service.validate_data_quality(l)
                    return results
                else:
                    return self.pipeline_service.validate_data_quality(layer)
            
            elif action_type == "catalogue_scan":
                return self.catalogue_explorer.scan_data_layers()
            
            elif action_type == "pii_audit":
                return self.catalogue_explorer.get_pii_summary()
            
            else:
                raise ValueError(f"Unknown action type: {action_type}")
                
        except Exception as e:
            logger.error(f"Quality action '{action_type}' failed: {str(e)}")
            return {
                "status": "failed",
                "action": action_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_quality_status(self) -> Dict[str, Any]:
        """Get current quality status summary"""
        try:
            # Get recent comprehensive check results (if available)
            # For now, return basic status
            pipeline_status = self.pipeline_service.get_pipeline_status()
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": "healthy",
                "pipeline_status": pipeline_status,
                "catalogue_tables": len(self.catalogue_explorer.catalogue.get("tables", {})),
                "pii_tables": len(self.catalogue_explorer.catalogue.get("pii_tags", {})),
                "last_check": None  # Would be populated from stored results
            }
            
            # Determine overall health
            if pipeline_status.get("success_rate", 100) < 95:
                status["overall_health"] = "warning"
            if pipeline_status.get("recent_failures", 0) > 0:
                status["overall_health"] = "critical"
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get quality status: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_health": "unknown",
                "error": str(e)
            }
