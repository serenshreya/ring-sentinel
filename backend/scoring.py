from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
import numpy as np

_model = None

def extract_cluster_features(cluster: dict, orders: list[dict]) -> list[float]:
    """
    Computes numerical risk signals for a cluster of accounts:
    1. device_sharing: 1.0 - (unique_devices / cluster_size)
    2. bank_sharing: 1.0 - (unique_refund_banks / cluster_size)
    3. ip_sharing: 1.0 - (unique_ips / cluster_size)
    4. avg_amount_scaled: average order amount in cluster / 100.0
    5. order_velocity: total orders / cluster_size
    6. cluster_size: count of unique accounts in the cluster
    """
    members = set(cluster.get('member_customer_ids', []))
    cluster_orders = [o for o in orders if o.get('customer_id') in members]
    
    devices = set(o.get('device_id') for o in cluster_orders if o.get('device_id'))
    ips = set(o.get('ip_address') for o in cluster_orders if o.get('ip_address'))
    banks = set(o.get('refund_bank_account') for o in cluster_orders if o.get('refund_bank_account'))
    amounts = [float(o.get('amount', 0)) for o in cluster_orders]
    
    c_size = max(1, len(members))
    dev_sharing = max(0.0, 1.0 - (len(devices) / c_size))
    bank_sharing = max(0.0, 1.0 - (len(banks) / c_size))
    ip_sharing = max(0.0, 1.0 - (len(ips) / c_size))
    avg_amt = float(np.mean(amounts)) if amounts else 65.0
    velocity = len(cluster_orders) / c_size
    
    return [
        dev_sharing,
        bank_sharing,
        ip_sharing,
        avg_amt / 100.0,
        velocity,
        float(c_size)
    ]

def train_and_score(clusters: list[dict], orders: list[dict], is_training: bool = True) -> list[dict]:
    """
    Trains on historical training clusters (orders in first 80% of timeline)
    and computes calibrated risk scores across all detected clusters.
    """
    global _model
    
    if not clusters:
        return clusters

    # Sort orders chronologically to cleanly identify training history
    sorted_orders = sorted(orders, key=lambda x: str(x.get('order_timestamp', '')))
    split_idx = int(len(sorted_orders) * 0.8)
    train_orders = sorted_orders[:split_idx]
    train_custs = set(o.get('customer_id') for o in train_orders)
    
    if is_training or _model is None:
        X_train = []
        y_train = []
        
        for c in clusters:
            members = set(c.get('member_customer_ids', []))
            # If cluster accounts have orders in the training period, use them for training
            c_train_orders = [o for o in train_orders if o.get('customer_id') in members]
            
            if c_train_orders:
                frauds = [1 for o in c_train_orders if o.get('is_fraud_label')]
                fraud_rate = len(frauds) / len(c_train_orders)
                
                feats = extract_cluster_features(c, train_orders)
                X_train.append(feats)
                # Label: 1 if majority fraud ring, 0 if innocent household/address collision
                y_train.append(1 if fraud_rate > 0.5 else 0)
                
        if len(set(y_train)) > 1:
            # Calibrated Logistic Regression provides smooth, continuous probability scores
            _model = LogisticRegression(C=1.5, max_iter=200, random_state=42)
            _model.fit(X_train, y_train)
        else:
            _model = None

    # Predict risk scores for all clusters using learned features
    for c in clusters:
        feats = extract_cluster_features(c, orders)
        if _model is not None:
            proba = _model.predict_proba([feats])[0]
            if 1 in _model.classes_:
                pos_idx = list(_model.classes_).index(1)
                score = float(proba[pos_idx])
            else:
                score = 0.5
        else:
            # Heuristic fallback based on strong signal sharing
            score = 0.85 if (feats[0] > 0.3 or feats[1] > 0.3) else 0.05
            
        c['risk_score'] = round(float(score), 4)
        
    return clusters

def compute_naive_baseline(orders: list[dict], threshold: float = 500.0) -> dict:
    tp, fp, tn, fn = 0, 0, 0, 0
    fp_cost = 0
    
    for o in orders:
        actual_fraud = bool(o.get('is_fraud_label'))
        pred_fraud = float(o.get('amount', 0)) > threshold
        
        if pred_fraud and actual_fraud:
            tp += 1
        elif pred_fraud and not actual_fraud:
            fp += 1
            fp_cost += 1
        elif not pred_fraud and not actual_fraud:
            tn += 1
        elif not pred_fraud and actual_fraud:
            fn += 1
            
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    
    return {
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1': round(f1, 4),
        'fpr': round(fpr, 4),
        'fp_cost': fp_cost,
        'tp': tp,
        'fp': fp,
        'tn': tn,
        'fn': fn
    }