import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class DataPipelineProcessor:
    """Processes data through bronze, silver, and gold layers"""
    
    def __init__(self, base_path: str = "docs"):
        self.base_path = Path(base_path)
        self.bronze_path = self.base_path / "bronze"
        self.silver_path = self.base_path / "silver"
        self.gold_path = self.base_path / "gold"
        
    def process_bronze_to_silver(self) -> Dict[str, pd.DataFrame]:
        """Transform raw bronze data to processed silver data"""
        logger.info("Starting bronze to silver transformation")
        
        # Process customers
        customers_df = self._process_customers()
        
        # Process transactions
        transactions_df = self._process_transactions()
        
        # Process products
        products_df = self._process_products()
        
        # Save silver layer data
        self._save_silver_data(customers_df, transactions_df, products_df)
        
        logger.info("Bronze to silver transformation completed")
        return {
            "customers": customers_df,
            "transactions": transactions_df,
            "products": products_df
        }
    
    def process_silver_to_gold(self) -> Dict[str, pd.DataFrame]:
        """Transform silver data to aggregated gold data"""
        logger.info("Starting silver to gold transformation")
        
        # Load silver data
        customers_df = pd.read_csv(self.silver_path / "processed_customers.csv")
        transactions_df = pd.read_csv(self.silver_path / "processed_transactions.csv")
        products_df = pd.read_csv(self.silver_path / "enriched_products.csv")
        
        # Generate gold layer insights
        segmentation_df = self._create_customer_segmentation(customers_df, transactions_df)
        performance_df = self._create_monthly_performance(transactions_df)
        product_perf_df = self._create_product_performance(transactions_df, products_df)
        
        # Save gold layer data
        self._save_gold_data(segmentation_df, performance_df, product_perf_df)
        
        logger.info("Silver to gold transformation completed")
        return {
            "segmentation": segmentation_df,
            "performance": performance_df,
            "product_performance": product_perf_df
        }
    
    def _process_customers(self) -> pd.DataFrame:
        """Process raw customer data"""
        customers_df = pd.read_csv(self.bronze_path / "raw_customer_data.csv")
        
        # Extract email domain
        customers_df['email_domain'] = customers_df['email'].str.split('@').str[1]
        
        # Create full name
        customers_df['full_name'] = customers_df['first_name'] + ' ' + customers_df['last_name']
        
        # Create age groups
        customers_df['age_group'] = pd.cut(
            customers_df['age'],
            bins=[0, 24, 34, 44, 100],
            labels=['18-24', '25-34', '35-44', '45+']
        ).fillna('18-24')
        
        # Create income tiers
        customers_df['income_tier'] = pd.cut(
            customers_df['income_level'],
            bins=[0, 50000, 80000, 100000, float('inf')],
            labels=['Low', 'Medium', 'High', 'Premium']
        ).fillna('Low')
        
        # Extract signup month and year
        customers_df['signup_date'] = pd.to_datetime(customers_df['signup_date'])
        customers_df['signup_month'] = customers_df['signup_date'].dt.month
        customers_df['signup_year'] = customers_df['signup_date'].dt.year
        
        # Select and reorder columns
        processed_df = customers_df[[
            'customer_id', 'email_domain', 'full_name', 'age_group', 
            'country', 'income_tier', 'signup_month', 'signup_year'
        ]]
        
        return processed_df
    
    def _process_transactions(self) -> pd.DataFrame:
        """Process raw transaction data"""
        transactions_df = pd.read_csv(self.bronze_path / "raw_transaction_data.csv")
        
        # Convert date and extract temporal features
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        transactions_df['day_of_week'] = transactions_df['transaction_date'].dt.day_name()
        transactions_df['quarter'] = transactions_df['transaction_date'].dt.quarter
        transactions_df['is_weekend'] = transactions_df['day_of_week'].isin(['Saturday', 'Sunday'])
        
        # Select and reorder columns
        processed_df = transactions_df[[
            'transaction_id', 'customer_id', 'transaction_date', 'amount',
            'product_category', 'payment_method', 'status', 'day_of_week',
            'quarter', 'is_weekend'
        ]]
        
        return processed_df
    
    def _process_products(self) -> pd.DataFrame:
        """Process raw product data"""
        products_df = pd.read_csv(self.bronze_path / "raw_product_data.csv")
        
        # Create price categories
        products_df['price_category'] = pd.cut(
            products_df['price'],
            bins=[0, 30, 70, 200, float('inf')],
            labels=['Budget', 'Medium', 'High', 'Premium']
        ).fillna('Budget')
        
        # Create stock status
        products_df['stock_status'] = np.where(
            products_df['stock_quantity'] > 50, 'In Stock', 'Low Stock'
        )
        
        # Extract launch year and calculate months since launch
        products_df['launch_date'] = pd.to_datetime(products_df['launch_date'])
        products_df['launch_year'] = products_df['launch_date'].dt.year
        current_date = datetime.now()
        products_df['months_since_launch'] = (
            (current_date.year - products_df['launch_year']) * 12 +
            (current_date.month - products_df['launch_date'].dt.month)
        )
        
        # Select and reorder columns
        processed_df = products_df[[
            'product_id', 'product_name', 'category', 'price', 'price_category',
            'supplier_id', 'stock_status', 'launch_year', 'months_since_launch'
        ]]
        
        return processed_df
    
    def _create_customer_segmentation(self, customers_df: pd.DataFrame, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Create customer segmentation analysis"""
        # Merge customer and transaction data
        merged_df = customers_df.merge(
            transactions_df[transactions_df['status'] == 'Completed'],
            on='customer_id',
            how='left'
        )
        
        # Calculate metrics per customer using silver layer features
        customer_metrics = merged_df.groupby('customer_id').agg({
            'income_tier': 'first',
            'amount': ['count', 'sum', 'mean'],
            'age_group': 'first'
        }).round(2)
        
        customer_metrics.columns = [
            'income_tier',
            'total_transactions',
            'total_revenue',
            'avg_transaction_value',
            'age_group'
        ]
        
        # Create segments
        segments = []
        for _, customer in customer_metrics.iterrows():
            if customer['income_tier'] in ['Premium', 'High'] and customer['total_transactions'] >= 3:
                segment = 'High_Value_Customers'
            elif customer['income_tier'] in ['Premium', 'High']:
                segment = 'Medium_Value_Customers'
            elif customer['income_tier'] == 'Low':
                segment = 'Low_Value_Customers'
            elif customer['age_group'] in ['18-24', '25-34']:
                segment = 'Young_Professionals'
            else:
                segment = 'Experienced_Professionals'
            
            segments.append(segment)
        
        customer_metrics['segment'] = segments
        
        # Aggregate by segment
        segmentation_df = customer_metrics.groupby('segment').agg({
            'total_transactions': 'sum',
            'total_revenue': 'sum',
            'avg_transaction_value': 'mean',
            'income_tier': 'first'
        }).round(2)
        
        segmentation_df['customer_count'] = customer_metrics.groupby('segment').size()
        segmentation_df['revenue_per_customer'] = (
            segmentation_df['total_revenue'] / segmentation_df['customer_count']
        ).round(2)
        
        return segmentation_df.reset_index()
    
    def _create_monthly_performance(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Create monthly performance metrics"""
        completed_tx = transactions_df[transactions_df['status'] == 'Completed'].copy()
        
        # Convert transaction_date to datetime if it's not already
        completed_tx['transaction_date'] = pd.to_datetime(completed_tx['transaction_date'])
        
        # Extract month and year
        completed_tx['month'] = completed_tx['transaction_date'].dt.month
        completed_tx['year'] = completed_tx['transaction_date'].dt.year
        
        # Aggregate metrics
        performance_df = completed_tx.groupby(['month', 'year']).agg({
            'amount': ['sum', 'count', 'mean'],
            'customer_id': 'nunique',
            'status': lambda x: (x == 'Completed').mean() * 100
        }).round(2)
        
        performance_df.columns = ['total_revenue', 'total_transactions', 'avg_transaction_value', 'unique_customers', 'success_rate']
        
        # Find top category
        top_category = completed_tx.groupby(['month', 'year', 'product_category'])['amount'].sum().reset_index()
        top_category = top_category.loc[top_category.groupby(['month', 'year'])['amount'].idxmax()]
        top_category = top_category.set_index(['month', 'year'])['product_category']
        
        performance_df['top_category'] = top_category
        
        return performance_df.reset_index()
    
    def _create_product_performance(self, transactions_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
        """Create product performance analysis"""
        completed_tx = transactions_df[transactions_df['status'] == 'Completed']
        
        # Aggregate by category
        product_perf_df = completed_tx.groupby('product_category').agg({
            'amount': ['sum', 'count', 'mean']
        }).round(2)
        
        product_perf_df.columns = ['total_revenue', 'total_units_sold', 'avg_price']
        
        # Find best selling product per category
        best_selling = completed_tx.groupby('product_category')['amount'].sum().reset_index()
        best_selling = best_selling.merge(
            products_df[['product_id', 'product_name', 'category']], 
            left_on='product_category', 
            right_on='category',
            how='left'
        )
        best_selling = best_selling.loc[best_selling.groupby('product_category')['amount'].idxmax()]
        
        product_perf_df['best_selling_product'] = best_selling.set_index('product_category')['product_name']
        
        # Calculate revenue share
        total_revenue = product_perf_df['total_revenue'].sum()
        product_perf_df['revenue_share'] = (product_perf_df['total_revenue'] / total_revenue * 100).round(1)
        
        return product_perf_df.reset_index()
    
    def _save_silver_data(self, customers_df: pd.DataFrame, transactions_df: pd.DataFrame, products_df: pd.DataFrame):
        """Save processed silver layer data"""
        self.silver_path.mkdir(exist_ok=True)
        
        customers_df.to_csv(self.silver_path / "processed_customers.csv", index=False)
        transactions_df.to_csv(self.silver_path / "processed_transactions.csv", index=False)
        products_df.to_csv(self.silver_path / "enriched_products.csv", index=False)
        
        logger.info(f"Silver data saved to {self.silver_path}")
    
    def _save_gold_data(self, segmentation_df: pd.DataFrame, performance_df: pd.DataFrame, product_perf_df: pd.DataFrame):
        """Save aggregated gold layer data"""
        self.gold_path.mkdir(exist_ok=True)
        
        segmentation_df.to_csv(self.gold_path / "customer_segmentation.csv", index=False)
        performance_df.to_csv(self.gold_path / "monthly_performance_metrics.csv", index=False)
        product_perf_df.to_csv(self.gold_path / "product_performance.csv", index=False)
        
        logger.info(f"Gold data saved to {self.gold_path}")
    
    def run_full_pipeline(self) -> Dict[str, Dict[str, pd.DataFrame]]:
        """Run the complete data pipeline"""
        logger.info("Starting full data pipeline execution")
        
        results = {}
        
        # Bronze to Silver
        results['silver'] = self.process_bronze_to_silver()
        
        # Silver to Gold
        results['gold'] = self.process_silver_to_gold()
        
        logger.info("Full data pipeline execution completed")
        return results
