import requests, os
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv('D:/ring-sentinel/.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_ANON_KEY')

auth_res = requests.post(f'{url}/auth/v1/token?grant_type=password',
    headers={'apikey': key, 'Content-Type': 'application/json'},
    json={'email': 'analyst@ringsentinel.com', 'password': 'Test1234!'}
)
token = auth_res.json()['access_token']
headers = {'apikey': key, 'Authorization': f'Bearer {token}'}

# Fetch all orders
all_orders = []
offset = 0
while True:
    res = requests.get(f'{url}/rest/v1/orders?select=*&offset={offset}&limit=1000', headers=headers).json()
    all_orders.extend(res)
    if len(res) < 1000:
        break
    offset += 1000

print(f'=== 1. DATASET OVERVIEW ===')
print(f'Total orders in DB: {len(all_orders)}')

# Sort by order_timestamp
all_orders.sort(key=lambda x: str(x.get('order_timestamp', '')))
split_idx = int(len(all_orders) * 0.8)
train_orders = all_orders[:split_idx]
test_orders = all_orders[split_idx:]

print(f'Train orders: {len(train_orders)}, Test orders: {len(test_orders)}')

# 1. Check entity overlap between train and test
print(f'\n=== 2. DATA LEAKAGE ANALYSIS (TRAIN vs HELD-OUT TEST) ===')
train_custs = set(o['customer_id'] for o in train_orders)
test_custs = set(o['customer_id'] for o in test_orders)
overlap_custs = train_custs.intersection(test_custs)
print(f'Customer IDs: Train={len(train_custs)}, Test={len(test_custs)}, OVERLAP={len(overlap_custs)}')

train_devs = set(o['device_id'] for o in train_orders)
test_devs = set(o['device_id'] for o in test_orders)
overlap_devs = train_devs.intersection(test_devs)
print(f'Device IDs:   Train={len(train_devs)}, Test={len(test_devs)}, OVERLAP={len(overlap_devs)}')

train_ips = set(o['ip_address'] for o in train_orders)
test_ips = set(o['ip_address'] for o in test_orders)
overlap_ips = train_ips.intersection(test_ips)
print(f'IP Addresses: Train={len(train_ips)}, Test={len(test_ips)}, OVERLAP={len(overlap_ips)}')

train_banks = set(o['refund_bank_account'] for o in train_orders)
test_banks = set(o['refund_bank_account'] for o in test_orders)
overlap_banks = train_banks.intersection(test_banks)
print(f'Refund Banks: Train={len(train_banks)}, Test={len(test_banks)}, OVERLAP={len(overlap_banks)}')

# 2. Check fraud orders in test set: are they all from overlapping entities?
test_fraud_orders = [o for o in test_orders if o['is_fraud_label']]
print(f'\nTest Fraud Orders: {len(test_fraud_orders)}')
test_fraud_custs = set(o['customer_id'] for o in test_fraud_orders)
test_fraud_devs = set(o['device_id'] for o in test_fraud_orders)
test_fraud_banks = set(o['refund_bank_account'] for o in test_fraud_orders)

print(f'  Fraud customer IDs in test that appeared in train: {len(test_fraud_custs.intersection(train_custs))}/{len(test_fraud_custs)}')
print(f'  Fraud devices in test that appeared in train: {len(test_fraud_devs.intersection(train_devs))}/{len(test_fraud_devs)}')
print(f'  Fraud refund banks in test that appeared in train: {len(test_fraud_banks.intersection(train_banks))}/{len(test_fraud_banks)}')

# 3. Check clusters in DB and score distribution
print(f'\n=== 3. CLUSTERS AND SCORE DISTRIBUTION ===')
clusters = requests.get(f'{url}/rest/v1/clusters?select=*', headers=headers).json()
print(f'Total clusters in DB: {len(clusters)}')
for c in clusters:
    cid = c['cluster_id']
    score = c['risk_score']
    status = c['status']
    m_ids = set(c['member_customer_ids'])
    c_orders = [o for o in all_orders if o['customer_id'] in m_ids]
    frauds = [o for o in c_orders if o['is_fraud_label']]
    legit = [o for o in c_orders if not o['is_fraud_label']]
    print(f'  Cluster #{cid}: risk_score={score}, status={status}, accounts={len(m_ids)}, orders={len(c_orders)}, fraud={len(frauds)}, legit={len(legit)}')

# 4. Check if ANY legitimate orders belong to any detected cluster
all_cluster_custs = set()
for c in clusters:
    all_cluster_custs.update(c['member_customer_ids'])

legit_orders_in_clusters = [o for o in all_orders if not o['is_fraud_label'] and o['customer_id'] in all_cluster_custs]
print(f'\n=== 4. FALSE POSITIVE GROUND TRUTH IN GRAPH ===')
print(f'Legitimate orders captured in any cluster: {len(legit_orders_in_clusters)} (Expected non-zero if realistic overlap)')

# 5. Check Innocent Overlap group behavior
innocent_orders = [o for o in all_orders if 'Shared Apt' in str(o.get('delivery_address', ''))]
print(f'Innocent overlap orders in DB: {len(innocent_orders)}')
innocent_custs = set(o['customer_id'] for o in innocent_orders)
innocent_in_clusters = innocent_custs.intersection(all_cluster_custs)
print(f'Innocent overlap customers captured in clusters: {len(innocent_in_clusters)}/{len(innocent_custs)}')
