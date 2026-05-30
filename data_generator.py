import pandas as pd
import numpy as np
from faker import Faker
import random
from tqdm import tqdm

fake = Faker()
np.random.seed(42)
random.seed(42)

NUM_CUSTOMERS = 1000
NUM_TRANSACTIONS = 15000
NUM_SESSIONS = 30000

def generate_skewed_ids(n_ids, size):
    weights = np.random.zipf(2, n_ids)
    weights = weights / weights.sum()
    return np.random.choice(np.arange(1, n_ids + 1), size=size, p=weights)

print("Generating customers...")
customers = []
for i in tqdm(range(1, NUM_CUSTOMERS + 1)):
    name = fake.name()
    email = f"{name.lower().replace(' ', '.')}@gmail.com"
    country = "Nigeria" if random.random() > 0.03 else None
    created_at = fake.date_time_between(start_date='-3y', end_date='-6m')
    customers.append([i, name, email, country, created_at])

df_customers = pd.DataFrame(customers, columns=["customer_id","name","email","country","created_at"])
df_customers = pd.concat([df_customers, df_customers.sample(frac=0.01)])
df_customers.to_csv("src_customers.csv", index=False)
print("Customers done!")

print("Generating transactions...")
customer_ids = generate_skewed_ids(NUM_CUSTOMERS, NUM_TRANSACTIONS)
transactions = []
for i in tqdm(range(1, NUM_TRANSACTIONS + 1)):
    amount = round(np.random.exponential(scale=2000), 2)
    if random.random() < 0.03:
        amount = None
    tx_time = fake.date_time_between(start_date='-1y', end_date='now')
    transactions.append([i, int(customer_ids[i-1]), amount, tx_time])

transactions += random.sample(transactions, int(0.02 * NUM_TRANSACTIONS))
df_transactions = pd.DataFrame(transactions, columns=["transaction_id","customer_id","amount","transaction_date"])
df_transactions.to_csv("src_billing_transactions.csv", index=False)
print("Transactions done!")

print("Generating sessions...")
customer_ids_s = generate_skewed_ids(NUM_CUSTOMERS, NUM_SESSIONS)
sessions = []
for i in tqdm(range(1, NUM_SESSIONS + 1)):
    start = fake.date_time_between(start_date='-1y', end_date='now')
    duration = random.randint(10, 1800)
    end = start + pd.Timedelta(seconds=duration)
    if random.random() < 0.02:
        end = start - pd.Timedelta(seconds=random.randint(1, 300))
    data_used = round(duration * random.uniform(0.01, 0.2), 2)
    if random.random() < 0.02:
        data_used = None
    sessions.append([i, int(customer_ids_s[i-1]), start, end, data_used])

sessions += random.sample(sessions, int(0.02 * NUM_SESSIONS))
df_sessions = pd.DataFrame(sessions, columns=["session_id","customer_id","start_time","end_time","data_used_mb"])
df_sessions.to_csv("src_network_sessions.csv", index=False)
print("Sessions done!")

print("DATA GENERATION COMPLETE!")
print("Files: src_customers.csv, src_billing_transactions.csv, src_network_sessions.csv")
