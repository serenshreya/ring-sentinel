import pandas as pd
import numpy as np
import uuid
import random
from datetime import datetime, timedelta

def get_insert_batches(orders: list[dict], batch_size: int = 200) -> list[list[dict]]:
    return [orders[i:i + batch_size] for i in range(0, len(orders), batch_size)]

def generate_all_orders() -> tuple[list[dict], list[dict]]:
    df = pd.read_csv('D:\\ring-sentinel\\credit_card_fraud_10k.csv')
    
    fraud_df = df[df['is_fraud'] == 1]
    legit_df = df[df['is_fraud'] == 0]
    
    fraud_mean = float(fraud_df['amount'].mean()) if not fraud_df.empty else 450.0
    fraud_std = float(fraud_df['amount'].std()) if not fraud_df.empty else 120.0
    
    legit_mean = float(legit_df['amount'].mean()) if not legit_df.empty else 65.0
    legit_std = float(legit_df['amount'].std()) if not legit_df.empty else 25.0
    
    start_date = datetime(2024, 1, 1)
    split_cutoff_days = 24.0  # First 24 days = 80% train, last 6 days = 20% test
    
    train_orders = []
    test_orders = []
    
    # -------------------------------------------------------------
    # 1. NORMAL ORDERS (1,800 orders = 90% of dataset)
    # Each normal customer has completely unique device, IP, bank, and home address
    # -------------------------------------------------------------
    for i in range(1800):
        day_offset = random.uniform(0, 30)
        ts = start_date + timedelta(days=day_offset, seconds=random.randint(0, 86400))
        amt = max(5.0, round(float(np.random.normal(legit_mean, legit_std)), 2))
        
        order = {
            'customer_id': f"CUST-N-{uuid.uuid4().hex[:8]}",
            'device_id': f"DEV-N-{uuid.uuid4().hex[:8]}",
            'ip_address': f"{random.randint(11,200)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'delivery_address': f"{i+1} Oak Wood Rd, Apt {random.randint(1, 999)}, District {random.randint(1, 50)}",
            'refund_bank_account': f"BANK-N-{uuid.uuid4().hex[:8]}",
            'amount': amt,
            'order_timestamp': ts.isoformat(),
            'is_fraud_label': False
        }
        if day_offset < split_cutoff_days:
            train_orders.append(order)
        else:
            test_orders.append(order)

    # -------------------------------------------------------------
    # 2. FRAUD RINGS (160 orders = 8% of dataset, 6 rings total)
    # -------------------------------------------------------------
    # RINGS 1-4: STRICTLY IN TRAINING PERIOD (Days 0 to 24)
    # 4 rings * 27 orders = 108 orders
    for r in range(4):
        num_cust = random.randint(5, 8)
        custs = [f"CUST-R{r+1}-{uuid.uuid4().hex[:6]}" for _ in range(num_cust)]
        shared_devs = [f"DEV-R{r+1}-{uuid.uuid4().hex[:6]}" for _ in range(random.randint(1, 2))]
        shared_ips = [f"10.{r+1}.0.{random.randint(10, 50)}" for _ in range(random.randint(1, 2))]
        shared_bank = f"BANK-R{r+1}-{uuid.uuid4().hex[:8]}"
        
        for _ in range(27):
            day_offset = random.uniform(0.5, split_cutoff_days - 0.5)
            ts = start_date + timedelta(days=day_offset, seconds=random.randint(0, 86400))
            amt = max(20.0, round(float(np.random.normal(fraud_mean, fraud_std)), 2))
            
            train_orders.append({
                'customer_id': random.choice(custs),
                'device_id': random.choice(shared_devs),
                'ip_address': random.choice(shared_ips),
                'delivery_address': f"{random.randint(100,999)} Ring Lane, Zone {r+1}",
                'refund_bank_account': shared_bank,
                'amount': amt,
                'order_timestamp': ts.isoformat(),
                'is_fraud_label': True
            })

    # RINGS 5-6: STRICTLY IN TEST PERIOD (Days 24 to 30) - BRAND NEW UNSEEN RINGS!
    # 2 rings * 26 orders = 52 orders (108 + 52 = 160 total fraud orders)
    for r in range(4, 6):
        num_cust = random.randint(5, 8)
        custs = [f"CUST-NOVEL-R{r+1}-{uuid.uuid4().hex[:6]}" for _ in range(num_cust)]
        shared_devs = [f"DEV-NOVEL-R{r+1}-{uuid.uuid4().hex[:6]}" for _ in range(random.randint(1, 2))]
        shared_ips = [f"192.168.{r+1}.{random.randint(10, 50)}" for _ in range(random.randint(1, 2))]
        shared_bank = f"BANK-NOVEL-R{r+1}-{uuid.uuid4().hex[:8]}"
        
        for _ in range(26):
            day_offset = random.uniform(split_cutoff_days + 0.2, 29.8)
            ts = start_date + timedelta(days=day_offset, seconds=random.randint(0, 86400))
            amt = max(20.0, round(float(np.random.normal(fraud_mean, fraud_std)), 2))
            
            test_orders.append({
                'customer_id': random.choice(custs),
                'device_id': random.choice(shared_devs),
                'ip_address': random.choice(shared_ips),
                'delivery_address': f"{random.randint(100,999)} Novel Ring Rd, Zone {r+1}",
                'refund_bank_account': shared_bank,
                'amount': amt,
                'order_timestamp': ts.isoformat(),
                'is_fraud_label': True
            })

    # -------------------------------------------------------------
    # 3. INNOCENT OVERLAP (40 orders = 2% of dataset, 8 groups of 5)
    # Shared delivery address (e.g. university hostel / apartment block)
    # BUT independent devices, IPs, and bank accounts!
    # -------------------------------------------------------------
    # Groups 1-5 in train period, Groups 6-8 in test period
    for g in range(8):
        hostel_address = f"University Residence Hall {chr(65 + g)}, 500 Campus Ave"
        in_train = g < 5
        num_in_group = 5
        
        for m in range(num_in_group):
            if in_train:
                day_offset = random.uniform(1.0, split_cutoff_days - 1.0)
            else:
                day_offset = random.uniform(split_cutoff_days + 0.5, 29.5)
                
            ts = start_date + timedelta(days=day_offset, seconds=random.randint(0, 86400))
            amt = max(5.0, round(float(np.random.normal(legit_mean, legit_std)), 2))
            
            order = {
                'customer_id': f"CUST-STUDENT-G{g+1}-{m+1}-{uuid.uuid4().hex[:4]}",
                'device_id': f"DEV-STUDENT-{uuid.uuid4().hex[:8]}",
                'ip_address': f"{random.randint(50,90)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                'delivery_address': hostel_address,
                'refund_bank_account': f"BANK-STUDENT-{uuid.uuid4().hex[:8]}",
                'amount': amt,
                'order_timestamp': ts.isoformat(),
                'is_fraud_label': False
            }
            if in_train:
                train_orders.append(order)
            else:
                test_orders.append(order)

    # Sort each list chronologically
    train_orders.sort(key=lambda x: x['order_timestamp'])
    test_orders.sort(key=lambda x: x['order_timestamp'])
    
    return train_orders, test_orders