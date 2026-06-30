import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "fact_pipeline.csv"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

np.random.seed(42)
n_opportunities = 2500

# More realistic SaaS B2B deal sizes
data = {
    'opportunity_id': range(10000, 10000 + n_opportunities),
    'account_id': np.random.randint(1000, 5000, n_opportunities),
    'stage': np.random.choice(
        ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost'],
        n_opportunities,
        p=[0.15, 0.20, 0.25, 0.20, 0.10, 0.10]
    ),
    'amount': np.random.randint(4000, 42000, n_opportunities),   # Realistic range
    'created_date': [datetime(2024, 1, 1) + timedelta(days=random.randint(0, 540)) for _ in range(n_opportunities)],
    'close_date': [datetime(2024, 1, 1) + timedelta(days=random.randint(30, 600)) for _ in range(n_opportunities)],
}

pipeline = pd.DataFrame(data)
pipeline['is_closed_won'] = pipeline['stage'] == 'Closed Won'

pipeline.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Realistic pipeline data generated")
print(f"Total pipeline value: ${pipeline['amount'].sum():,.0f}")
print(f"Average deal size: ${pipeline['amount'].mean():,.0f}")