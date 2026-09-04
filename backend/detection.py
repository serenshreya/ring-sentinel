import networkx as nx
from collections import defaultdict

def detect_clusters(orders: list[dict]) -> list[dict]:
    """
    Constructs an identity graph across accounts based on shared signals:
    - device_id (Hardware fingerprint)
    - ip_address (Network fingerprint)
    - refund_bank_account (Financial beneficiary fingerprint)
    - delivery_address (Physical shipping address)
    
    Connected components of size > 1 form candidate clusters.
    """
    G = nx.Graph()
    
    # Map signals to customer_ids
    device_to_custs = defaultdict(set)
    ip_to_custs = defaultdict(set)
    bank_to_custs = defaultdict(set)
    addr_to_custs = defaultdict(set)
    
    for order in orders:
        cust = order.get('customer_id')
        if not cust:
            continue
        G.add_node(cust)
        
        dev = order.get('device_id')
        if dev:
            device_to_custs[dev].add(cust)
            
        ip = order.get('ip_address')
        if ip:
            ip_to_custs[ip].add(cust)
            
        bank = order.get('refund_bank_account')
        if bank:
            bank_to_custs[bank].add(cust)
            
        addr = order.get('delivery_address')
        if addr:
            addr_to_custs[addr].add(cust)
            
    # Connect customers sharing ANY signal
    for signal_dict in (device_to_custs, ip_to_custs, bank_to_custs, addr_to_custs):
        for custs in signal_dict.values():
            if len(custs) > 1:
                cust_list = list(custs)
                root = cust_list[0]
                for other in cust_list[1:]:
                    G.add_edge(root, other)
                    
    components = list(nx.connected_components(G))
    clusters = []
    
    for comp in components:
        if len(comp) > 1:
            clusters.append({
                'member_customer_ids': list(comp),
                'risk_score': 0.0,
                'status': 'pending'
            })
            
    return clusters