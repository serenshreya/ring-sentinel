import os
import requests
from dotenv import load_dotenv
from seed_data import generate_all_orders, get_insert_batches

load_dotenv('D:/ring-sentinel/.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_ANON_KEY')

print("Authenticating with Supabase...")
auth_res = requests.post(f"{url}/auth/v1/token?grant_type=password",
    headers={"apikey": key, "Content-Type": "application/json"},
    json={"email": "analyst@ringsentinel.com", "password": "Test1234!"}
)
token = auth_res.json()["access_token"]
headers = {
    "apikey": key,
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

print("1. Clearing existing clusters...")
requests.delete(f"{url}/rest/v1/clusters?cluster_id=neq.0", headers=headers)

print("2. Clearing existing orders...")
requests.delete(f"{url}/rest/v1/orders?order_id=neq.0", headers=headers)

print("3. Generating new leak-free realistic orders...")
train_orders, test_orders = generate_all_orders()
all_orders = train_orders + test_orders
batches = get_insert_batches(all_orders, batch_size=200)

print(f"4. Inserting {len(all_orders)} orders in {len(batches)} batches...")
for idx, batch in enumerate(batches):
    res = requests.post(f"{url}/rest/v1/orders", headers=headers, json=batch)
    if res.status_code not in (200, 201):
        print(f"   Batch {idx+1} failed: {res.status_code}, {res.text}")
    else:
        print(f"   Batch {idx+1}/{len(batches)} inserted ({len(batch)} orders)")

print("5. Verifying order count in Supabase...")
count_res = requests.get(f"{url}/rest/v1/orders?select=count", headers={
    "apikey": key,
    "Authorization": f"Bearer {token}",
    "Range-Unit": "items"
})
print("Orders insert complete!")