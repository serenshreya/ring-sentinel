import os, sys, time
from dotenv import load_dotenv
from supabase import create_client
from seed_data import generate_all_orders, get_insert_batches

load_dotenv('D:/ring-sentinel/.env')
url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_ANON_KEY')

supabase = create_client(url, key)

# Sign in to get authenticated session for RLS
login_res = supabase.auth.sign_in_with_password({'email': 'analyst@ringsentinel.com', 'password': 'Test1234!'})
print(f'Logged in as: {login_res.user.email}')

print('Generating 2,000 synthetic orders from CSV distribution...')
train_orders, test_orders = generate_all_orders()
all_orders = train_orders + test_orders
print(f'Total orders to insert: {len(all_orders)}')

batches = get_insert_batches(all_orders, batch_size=100)
inserted = 0

for i, batch in enumerate(batches):
    for retry in range(3):
        try:
            supabase.table('orders').insert(batch).execute()
            inserted += len(batch)
            print(f'Batch {i+1}/{len(batches)} inserted ({inserted}/{len(all_orders)})')
            break
        except Exception as e:
            print(f'Retry {retry+1} for batch {i+1}: {e}')
            time.sleep(1)

print(f'Finished inserting {inserted} records!')
