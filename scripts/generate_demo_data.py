#!/usr/bin/env python3
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

BASE_PATH = Path(__file__).resolve().parent.parent
DOCS_PATH = BASE_PATH / "docs"
BRONZE_PATH = DOCS_PATH / "bronze"

CUSTOMER_COUNTRIES = ["United States", "Canada", "United Kingdom", "Germany", "Australia"]
PRODUCT_CATEGORIES = ["Electronics", "Home", "Sports", "Beauty", "Office"]
PAYMENT_METHODS = ["Credit Card", "PayPal", "Wire Transfer", "Debit Card"]
TRANSACTION_STATUS = ["Completed", "Failed", "Pending"]
FIRST_NAMES = ["Avery", "Jordan", "Taylor", "Morgan", "Riley", "Hayden", "Skyler", "Casey", "Jamie", "Quinn"]
LAST_NAMES = ["Smith", "Johnson", "Brown", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin"]


def _ensure_directories():
    BRONZE_PATH.mkdir(parents=True, exist_ok=True)


def _random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate_customers(count: int = 50):
    customers = []
    for customer_id in range(1, count + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}{customer_id}@example.com"
        age = random.randint(18, 70)
        income_level = random.choice([40000, 55000, 75000, 95000, 120000])
        signup_date = _random_date(datetime(2020, 1, 1), datetime(2023, 12, 31)).strftime("%Y-%m-%d")
        country = random.choice(CUSTOMER_COUNTRIES)
        phone = f"+1-{random.randint(200, 999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        customers.append({
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "age": age,
            "income_level": income_level,
            "signup_date": signup_date,
            "country": country,
            "phone": phone
        })
    return pd.DataFrame(customers)


def generate_products(count: int = 20):
    products = []
    for product_id in range(1, count + 1):
        category = random.choice(PRODUCT_CATEGORIES)
        product_name = f"{category} Item {product_id}"
        price = round(random.uniform(10, 250), 2)
        supplier_id = random.randint(100, 199)
        stock_quantity = random.randint(5, 120)
        launch_date = _random_date(datetime(2019, 1, 1), datetime(2024, 3, 31)).strftime("%Y-%m-%d")
        products.append({
            "product_id": product_id,
            "product_name": product_name,
            "category": category,
            "price": price,
            "supplier_id": supplier_id,
            "stock_quantity": stock_quantity,
            "launch_date": launch_date
        })
    return pd.DataFrame(products)


def generate_transactions(customers: pd.DataFrame, products: pd.DataFrame, count: int = 200):
    transactions = []
    for transaction_id in range(1, count + 1):
        customer = customers.sample(n=1).iloc[0]
        product = products.sample(n=1).iloc[0]
        transaction_date = _random_date(datetime(2023, 1, 1), datetime(2024, 3, 31)).strftime("%Y-%m-%d")
        amount = round(max(5.0, random.gauss(product["price"], 20)), 2)
        transactions.append({
            "transaction_id": transaction_id,
            "customer_id": int(customer["customer_id"]),
            "transaction_date": transaction_date,
            "amount": amount,
            "product_category": product["category"],
            "payment_method": random.choice(PAYMENT_METHODS),
            "status": random.choices(TRANSACTION_STATUS, weights=[0.7, 0.15, 0.15])[0]
        })
    return pd.DataFrame(transactions)


def main():
    _ensure_directories()

    customers = generate_customers()
    products = generate_products()
    transactions = generate_transactions(customers, products)

    customers.to_csv(BRONZE_PATH / "raw_customer_data.csv", index=False)
    products.to_csv(BRONZE_PATH / "raw_product_data.csv", index=False)
    transactions.to_csv(BRONZE_PATH / "raw_transaction_data.csv", index=False)

    print(f"Generated {len(customers)} customer rows, {len(products)} product rows, and {len(transactions)} transaction rows.")
    print(f"Files written to {BRONZE_PATH}")
    print("Run the pipeline with: python -m app.api.main or uvicorn app.api.main:app --reload --port 8000")


if __name__ == "__main__":
    main()
