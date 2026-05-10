import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from app.observability.metrics import (
    CATALOGUE_LINEAGE_RELATIONS_COUNT,
    CATALOGUE_PII_TABLE_COUNT,
    CATALOGUE_TABLES_COUNT
)

logger = logging.getLogger(__name__)

class DataCatalogueExplorer:
    """Explore and manage data catalogue with lineage tracking"""
    
    def __init__(self, base_path: str = "docs"):
        self.base_path = Path(base_path)
        self.catalogue_file = self.base_path / "data_catalogue.json"
        self._load_catalogue()
        
    def _load_catalogue(self):
        """Load existing catalogue or create new one"""
        if self.catalogue_file.exists():
            try:
                with open(self.catalogue_file, 'r') as f:
                    self.catalogue = json.load(f)
            except Exception as e:
                logger.error(f"Error loading catalogue: {e}")
                self.catalogue = self._create_default_catalogue()
        else:
            self.catalogue = self._create_default_catalogue()
            self._save_catalogue()
    
    def _create_default_catalogue(self) -> Dict[str, Any]:
        """Create default data catalogue structure"""
        return {
            "tables": {},
            "lineage": {},
            "pii_tags": {},
            "quality_metrics": {},
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_catalogue(self):
        """Save catalogue to file"""
        self.catalogue["last_updated"] = datetime.now().isoformat()
        with open(self.catalogue_file, 'w') as f:
            json.dump(self.catalogue, f, indent=2)
    
    def scan_data_layers(self) -> Dict[str, Any]:
        """Scan all data layers and update catalogue"""
        logger.info("Scanning data layers for catalogue update")
        
        # Scan bronze layer
        bronze_tables = self._scan_layer("bronze")
        
        # Scan silver layer
        silver_tables = self._scan_layer("silver")
        
        # Scan gold layer
        gold_tables = self._scan_layer("gold")
        
        # Update catalogue
        self.catalogue["tables"] = {
            **bronze_tables,
            **silver_tables,
            **gold_tables
        }
        
        # Update lineage
        self._update_lineage()
        
        # Add PII tags
        self._add_pii_tags()
        
        # Calculate quality metrics
        self._calculate_quality_metrics()
        
        # Publish catalogue metrics to Prometheus
        self._update_catalogue_metrics()
        
        self._save_catalogue()
        
        return {
            "status": "success",
            "tables_found": len(self.catalogue["tables"]),
            "layers_scanned": ["bronze", "silver", "gold"],
            "last_updated": self.catalogue["last_updated"]
        }
    
    def _scan_layer(self, layer: str) -> Dict[str, Any]:
        """Scan a specific data layer"""
        layer_path = self.base_path / layer
        tables = {}
        
        if not layer_path.exists():
            return tables
        
        for csv_file in layer_path.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                
                table_info = {
                    "name": csv_file.stem,
                    "layer": layer,
                    "file_path": str(csv_file),
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns),
                    "data_types": df.dtypes.astype(str).to_dict(),
                    "null_counts": df.isnull().sum().to_dict(),
                    "file_size": csv_file.stat().st_size,
                    "last_modified": datetime.fromtimestamp(csv_file.stat().st_mtime).isoformat(),
                    "sample_data": df.head(3).to_dict('records')
                }
                
                tables[f"{layer}.{csv_file.stem}"] = table_info
                
            except Exception as e:
                logger.error(f"Error scanning {csv_file}: {e}")
        
        return tables
    
    def _update_lineage(self):
        """Update data lineage information"""
        lineage = {
            "bronze_to_silver": {
                "source_tables": [],
                "target_tables": [],
                "transformations": []
            },
            "silver_to_gold": {
                "source_tables": [],
                "target_tables": [],
                "transformations": []
            }
        }
        
        # Bronze to Silver lineage
        bronze_tables = [k for k in self.catalogue["tables"].keys() if k.startswith("bronze.")]
        silver_tables = [k for k in self.catalogue["tables"].keys() if k.startswith("silver.")]
        
        lineage["bronze_to_silver"]["source_tables"] = bronze_tables
        lineage["bronze_to_silver"]["target_tables"] = silver_tables
        lineage["bronze_to_silver"]["transformations"] = [
            "Customer data enrichment (email domain, age groups, income tiers)",
            "Transaction temporal analysis (day of week, quarter, weekend flag)",
            "Product categorization (price categories, stock status)"
        ]
        
        # Silver to Gold lineage
        gold_tables = [k for k in self.catalogue["tables"].keys() if k.startswith("gold.")]
        
        lineage["silver_to_gold"]["source_tables"] = silver_tables
        lineage["silver_to_gold"]["target_tables"] = gold_tables
        lineage["silver_to_gold"]["transformations"] = [
            "Customer segmentation analysis",
            "Monthly performance metrics aggregation",
            "Product performance analytics"
        ]
        
        self.catalogue["lineage"] = lineage
    
    def _add_pii_tags(self):
        """Add PII (Personally Identifiable Information) tags"""
        pii_tags = {}
        
        for table_key, table_info in self.catalogue["tables"].items():
            table_pii = {}
            
            # Check for PII columns
            pii_columns = {
                "email": ["email"],
                "name": ["first_name", "last_name", "full_name"],
                "phone": ["phone"],
                "address": ["address", "street", "city", "zip"],
                "identifier": ["customer_id", "transaction_id", "product_id"]
            }
            
            for pii_type, columns in pii_columns.items():
                matching_cols = [col for col in columns if col in table_info["columns"]]
                if matching_cols:
                    table_pii[pii_type] = matching_cols
            
            if table_pii:
                pii_tags[table_key] = table_pii
        
        self.catalogue["pii_tags"] = pii_tags
    
    def _calculate_quality_metrics(self):
        """Calculate data quality metrics"""
        quality_metrics = {}
        
        for table_key, table_info in self.catalogue["tables"].items():
            metrics = {
                "completeness": 0.0,
                "uniqueness": 0.0,
                "validity": 0.0,
                "overall_score": 0.0
            }
            
            # Calculate completeness (percentage of non-null values)
            total_cells = table_info["row_count"] * table_info["column_count"]
            total_nulls = sum(table_info["null_counts"].values())
            metrics["completeness"] = round(((total_cells - total_nulls) / total_cells) * 100, 2)
            
            # Calculate uniqueness for ID columns
            id_columns = [col for col in table_info["columns"] if "id" in col.lower()]
            if id_columns:
                try:
                    df = pd.read_csv(table_info["file_path"])
                    uniqueness_scores = []
                    for col in id_columns:
                        unique_ratio = df[col].nunique() / len(df)
                        uniqueness_scores.append(unique_ratio * 100)
                    metrics["uniqueness"] = round(sum(uniqueness_scores) / len(uniqueness_scores), 2)
                except:
                    metrics["uniqueness"] = 0.0
            else:
                metrics["uniqueness"] = 100.0
            
            # Calculate validity (basic checks)
            metrics["validity"] = 100.0  # Assume valid unless specific validation rules are defined
            
            # Calculate overall score
            metrics["overall_score"] = round(
                (metrics["completeness"] + metrics["uniqueness"] + metrics["validity"]) / 3, 2
            )
            
            quality_metrics[table_key] = metrics
        
        self.catalogue["quality_metrics"] = quality_metrics
    
    def _update_catalogue_metrics(self):
        """Publish summary catalogue metrics for Grafana"""
        tables_count = len(self.catalogue["tables"])
        pii_table_count = len(self.catalogue["pii_tags"])
        lineage_relations = (
            len(self.catalogue["lineage"]["bronze_to_silver"]["source_tables"]) *
            len(self.catalogue["lineage"]["bronze_to_silver"]["target_tables"]) +
            len(self.catalogue["lineage"]["silver_to_gold"]["source_tables"]) *
            len(self.catalogue["lineage"]["silver_to_gold"]["target_tables"])
        )
        
        CATALOGUE_TABLES_COUNT.set(tables_count)
        CATALOGUE_PII_TABLE_COUNT.set(pii_table_count)
        CATALOGUE_LINEAGE_RELATIONS_COUNT.set(lineage_relations)
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific table"""
        for table_key, table_info in self.catalogue["tables"].items():
            if table_info["name"] == table_name or table_key == table_name:
                return {
                    **table_info,
                    "pii_tags": self.catalogue["pii_tags"].get(table_key, {}),
                    "quality_metrics": self.catalogue["quality_metrics"].get(table_key, {}),
                    "lineage": self._get_table_lineage(table_key)
                }
        return None
    
    def _get_table_lineage(self, table_key: str) -> Dict[str, Any]:
        """Get lineage information for a specific table"""
        lineage_info = {"upstream": [], "downstream": []}
        
        # Check if table is in bronze layer
        if table_key.startswith("bronze."):
            lineage_info["downstream"] = self.catalogue["lineage"]["bronze_to_silver"]["target_tables"]
        
        # Check if table is in silver layer
        elif table_key.startswith("silver."):
            lineage_info["upstream"] = self.catalogue["lineage"]["bronze_to_silver"]["source_tables"]
            lineage_info["downstream"] = self.catalogue["lineage"]["silver_to_gold"]["target_tables"]
        
        # Check if table is in gold layer
        elif table_key.startswith("gold."):
            lineage_info["upstream"] = self.catalogue["lineage"]["silver_to_gold"]["source_tables"]
        
        return lineage_info
    
    def search_tables(self, query: str, layer: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search tables by name or column"""
        results = []
        query_lower = query.lower()
        
        for table_key, table_info in self.catalogue["tables"].items():
            # Filter by layer if specified
            if layer and not table_key.startswith(f"{layer}."):
                continue
            
            # Search in table name
            if query_lower in table_info["name"].lower():
                results.append({
                    "table_key": table_key,
                    "match_type": "table_name",
                    "table_info": table_info
                })
                continue
            
            # Search in columns
            matching_columns = [col for col in table_info["columns"] if query_lower in col.lower()]
            if matching_columns:
                results.append({
                    "table_key": table_key,
                    "match_type": "column",
                    "matching_columns": matching_columns,
                    "table_info": table_info
                })
        
        return results
    
    def get_lineage_diagram(self) -> Dict[str, Any]:
        """Get lineage diagram data"""
        return {
            "nodes": [
                {
                    "id": table_key,
                    "name": table_info["name"],
                    "layer": table_info["layer"],
                    "type": "table"
                }
                for table_key, table_info in self.catalogue["tables"].items()
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "type": "transformation"
                }
                for source in self.catalogue["lineage"]["bronze_to_silver"]["source_tables"]
                for target in self.catalogue["lineage"]["bronze_to_silver"]["target_tables"]
            ] + [
                {
                    "source": source,
                    "target": target,
                    "type": "aggregation"
                }
                for source in self.catalogue["lineage"]["silver_to_gold"]["source_tables"]
                for target in self.catalogue["lineage"]["silver_to_gold"]["target_tables"]
            ]
        }
    
    def get_pii_summary(self) -> Dict[str, Any]:
        """Get summary of PII data across all tables"""
        pii_summary = {
            "total_tables_with_pii": len(self.catalogue["pii_tags"]),
            "pii_types": {},
            "high_risk_tables": []
        }
        
        # Count PII types
        for table_key, pii_tags in self.catalogue["pii_tags"].items():
            for pii_type in pii_tags.keys():
                if pii_type not in pii_summary["pii_types"]:
                    pii_summary["pii_types"][pii_type] = 0
                pii_summary["pii_types"][pii_type] += 1
        
        # Identify high-risk tables (with email or phone)
        for table_key, pii_tags in self.catalogue["pii_tags"].items():
            if any(pii_type in ["email", "phone"] for pii_type in pii_tags.keys()):
                pii_summary["high_risk_tables"].append({
                    "table": table_key,
                    "pii_types": list(pii_tags.keys())
                })
        
        return pii_summary
