# ADVISORY-ONLY SYSTEM: Ring Sentinel provides risk analysis and recommendations.
# It CANNOT move money, block payments, freeze accounts, or take ANY irreversible action.
# All outputs are advisory — human review is required before any action is taken.

import os
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
from supabase import create_client, Client

from auth import get_current_user
from models import OrderResponse, ClusterResponse, ClusterUpdateRequest, ExplanationResponse, CombinedMetricsResponse
from detection import detect_clusters
from scoring import train_and_score, compute_naive_baseline
from explain import generate_explanation
from metrics import compute_metrics
from seed_data import generate_all_orders, get_insert_batches

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise RuntimeError("Supabase credentials not found in environment variables.")

# Create base admin client for unauthenticated background stuff if needed
# but mostly we'll use authenticated client
base_supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ring-sentinel-ten.vercel.app",
    ],
    allow_origin_regex=r"https:\/\/ring-sentinel.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_auth_client(request: Request) -> Client:
    # Gets client with the user's token set
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="No authorization header")
        
    token = auth_header.replace("Bearer ", "")
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    # Using private _headers might be needed depending on supabase-py version
    # The standard way to set token on python client is:
    client.postgrest.auth(token)
    return client

@app.get("/health")
def health_check():
    return {"status": "ok"}

def fetch_all_orders(client):
    """Fetch all orders, bypassing Supabase's default 1000-row limit."""
    all_data = []
    page_size = 1000
    offset = 0
    while True:
        result = client.table('orders').select('*').range(offset, offset + page_size - 1).execute()
        all_data.extend(result.data)
        if len(result.data) < page_size:
            break
        offset += page_size
    return all_data

@app.get("/orders", response_model=list[OrderResponse])
@limiter.limit("30/minute")
def get_orders(request: Request, user: dict = Depends(get_current_user)):
    client = get_auth_client(request)
    return fetch_all_orders(client)

@app.post("/detect", response_model=list[ClusterResponse])
@limiter.limit("30/minute")
def detect(request: Request, user: dict = Depends(get_current_user)):
    client = get_auth_client(request)
    
    # fetch all orders (bypasses 1000-row limit)
    orders = fetch_all_orders(client)
    
    # run detection
    clusters = detect_clusters(orders)
    
    # clear existing clusters
    # Requires an ID to delete all, we can use neq filter
    client.table('clusters').delete().neq('cluster_id', 0).execute()
    
    inserted_clusters = []
    if clusters:
        # insert new
        res = client.table('clusters').insert(clusters).execute()
        inserted_clusters = res.data
        
    return inserted_clusters

@app.post("/score", response_model=list[ClusterResponse])
@limiter.limit("30/minute")
def score_clusters(request: Request, user: dict = Depends(get_current_user)):
    client = get_auth_client(request)
    
    orders = fetch_all_orders(client)
    
    clusters_res = client.table('clusters').select('*').execute()
    clusters = clusters_res.data
    
    # Score
    scored = train_and_score(clusters, orders)
    
    # Update risk_score in Supabase
    updated_clusters = []
    for c in scored:
        cid = c.get('cluster_id')
        score = c.get('risk_score', 0.0)
        res = client.table('clusters').update({'risk_score': score}).eq('cluster_id', cid).execute()
        if res.data:
            updated_clusters.extend(res.data)
            
    return updated_clusters if updated_clusters else scored

@app.get("/explain/{cluster_id}", response_model=ExplanationResponse)
@limiter.limit("30/minute")
def explain_cluster(cluster_id: int, request: Request, user: dict = Depends(get_current_user)):
    client = get_auth_client(request)
    
    cluster_res = client.table('clusters').select('*').eq('cluster_id', cluster_id).execute()
    if not cluster_res.data:
        raise HTTPException(status_code=404, detail="Cluster not found")
    cluster = cluster_res.data[0]
    
    orders_res = client.table('orders').select('*').in_('customer_id', cluster['member_customer_ids']).execute()
    orders = orders_res.data
    
    explanation = generate_explanation(cluster, orders)
    
    res = client.table('clusters').update({'explanation_text': explanation}).eq('cluster_id', cluster_id).execute()
    
    return {"cluster_id": cluster_id, "explanation_text": explanation}

@app.get("/metrics", response_model=CombinedMetricsResponse)
@limiter.limit("30/minute")
def get_metrics(request: Request, user: dict = Depends(get_current_user)):
    client = get_auth_client(request)
    
    orders = fetch_all_orders(client)
    
    clusters_res = client.table('clusters').select('*').execute()
    clusters = clusters_res.data
    
    metrics = compute_metrics(clusters, orders)
    return metrics

@app.patch("/clusters/{cluster_id}/status", response_model=ClusterResponse)
@limiter.limit("30/minute")
def update_cluster_status(cluster_id: int, body: ClusterUpdateRequest, request: Request, user: dict = Depends(get_current_user)):
    # ADVISORY ONLY: This status update is informational. This system CANNOT move money, block payments, or take any irreversible action.
    client = get_auth_client(request)
    
    res = client.table('clusters').update({'status': body.status}).eq('cluster_id', cluster_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Cluster not found")
        
    return res.data[0]

@app.post("/seed")
@limiter.limit("30/minute")
def seed_data(request: Request, user: dict = Depends(get_current_user)):
    client = get_auth_client(request)
    
    # clear existing orders
    client.table('orders').delete().neq('order_id', 0).execute()
    
    train_orders, test_orders = generate_all_orders()
    all_orders = train_orders + test_orders
    
    batches = get_insert_batches(all_orders)
    
    total_inserted = 0
    for batch in batches:
        res = client.table('orders').insert(batch).execute()
        total_inserted += len(res.data)
        
    return {"message": f"Successfully seeded {total_inserted} orders."}
