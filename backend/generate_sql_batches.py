import os, sys
sys.path.append('D:/ring-sentinel/backend')
from seed_data import generate_all_orders

os.makedirs('D:/ring-sentinel/backend/seed_sql', exist_ok=True)
train_orders, test_orders = generate_all_orders()
all_orders = train_orders + test_orders

batch_size = 500
for b_idx in range(0, len(all_orders), batch_size):
    batch = all_orders[b_idx:b_idx+batch_size]
    values = []
    for o in batch:
        c_id = o['customer_id'].replace("'", "''")
        d_id = o['device_id'].replace("'", "''")
        ip = o['ip_address'].replace("'", "''")
        addr = o['delivery_address'].replace("'", "''")
        bank = o['refund_bank_account'].replace("'", "''")
        amt = o['amount']
        ts = o['order_timestamp']
        fraud = 'true' if o['is_fraud_label'] else 'false'
        values.append(f"('{c_id}', '{d_id}', '{ip}', '{addr}', '{bank}', {amt}, '{ts}', {fraud})")
    sql = "INSERT INTO public.orders (customer_id, device_id, ip_address, delivery_address, refund_bank_account, amount, order_timestamp, is_fraud_label) VALUES\n" + ",\n".join(values) + ";"
    with open(f"D:/ring-sentinel/backend/seed_sql/batch_{b_idx//batch_size}.sql", "w", encoding="utf-8") as f:
        f.write(sql)
print("Generated 4 SQL files successfully!")
