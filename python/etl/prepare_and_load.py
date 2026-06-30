import pandas as pd
import numpy as np
import duckdb
from datetime import datetime, timedelta
from pathlib import Path
import random

np.random.seed(42)
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH = PROCESSED_DIR / "revenueforge.duckdb"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("Generating realistic synthetic SaaS data...")

# ====================== SYNTHETIC DATA ======================
n_accounts = 1200
n_subscriptions = 1800

# Accounts
accounts = pd.DataFrame({
    'account_id': range(1000, 1000 + n_accounts),
    'company_name': [f"Company {i}" for i in range(n_accounts)],
    'industry': np.random.choice(
        ['Technology', 'Finance', 'Healthcare', 'Retail', 'Manufacturing', 'Professional Services'], 
        n_accounts
    ),
    'created_at': [datetime(2023, 1, 1) + timedelta(days=random.randint(0, 900)) for _ in range(n_accounts)]
})

# Subscriptions
start_dates = [datetime(2024, 1, 1) + timedelta(days=random.randint(0, 540)) for _ in range(n_subscriptions)]
end_dates = []
for sd in start_dates:
    if random.random() < 0.65:  # ~65% still active
        end_dates.append(None)
    else:
        end_dates.append(sd + timedelta(days=random.randint(90, 450)))

subscriptions = pd.DataFrame({
    'subscription_id': range(50000, 50000 + n_subscriptions),
    'account_id': np.random.choice(accounts['account_id'], n_subscriptions),
    'plan_name': np.random.choice(['Starter', 'Professional', 'Enterprise'], n_subscriptions, p=[0.4, 0.45, 0.15]),
    'monthly_fee': np.random.choice([29, 79, 199, 499], n_subscriptions),
    'start_date': start_dates,
    'end_date': end_dates,
    'status': ['Active' if e is None else 'Churned' for e in end_dates]
})

subscriptions['mrr'] = subscriptions['monthly_fee']

# Load existing pipeline data
pipeline_path = PROCESSED_DIR / "fact_pipeline.csv"
if pipeline_path.exists():
    pipeline = pd.read_csv(pipeline_path)
    pipeline['created_date'] = pd.to_datetime(pipeline['created_date'])
    pipeline['close_date'] = pd.to_datetime(pipeline['close_date'])
else:
    print("Warning: fact_pipeline.csv not found. Run generate_pipeline_data.py first.")
    pipeline = pd.DataFrame()

print("Writing everything to DuckDB...")

con = duckdb.connect(str(DB_PATH))

con.execute("CREATE OR REPLACE TABLE dim_accounts AS SELECT * FROM accounts")
con.execute("CREATE OR REPLACE TABLE fact_subscriptions AS SELECT * FROM subscriptions")
if not pipeline.empty:
    con.execute("CREATE OR REPLACE TABLE fact_pipeline AS SELECT * FROM pipeline")

con.close()

print(f"✅ Synthetic data loaded successfully into {DB_PATH}")
print(f"   - {len(accounts)} accounts")
print(f"   - {len(subscriptions)} subscriptions")
if not pipeline.empty:
    print(f"   - {len(pipeline)} pipeline opportunities")