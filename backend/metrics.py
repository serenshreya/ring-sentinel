def evaluate_dataset(orders: list[dict], flagged_customers: set, naive_threshold: float = 500.0) -> dict:
    rs_tp, rs_fp, rs_tn, rs_fn = 0, 0, 0, 0
    rs_fp_cost = 0
    
    nb_tp, nb_fp, nb_tn, nb_fn = 0, 0, 0, 0
    nb_fp_cost = 0
    
    for o in orders:
        actual_fraud = bool(o.get('is_fraud_label'))
        
        # Ring Sentinel Prediction
        rs_pred = o.get('customer_id') in flagged_customers
        if rs_pred and actual_fraud:
            rs_tp += 1
        elif rs_pred and not actual_fraud:
            rs_fp += 1
            rs_fp_cost += 1
        elif not rs_pred and not actual_fraud:
            rs_tn += 1
        elif not rs_pred and actual_fraud:
            rs_fn += 1
            
        # Naive Baseline Prediction (any order amount > threshold)
        nb_pred = float(o.get('amount', 0)) > naive_threshold
        if nb_pred and actual_fraud:
            nb_tp += 1
        elif nb_pred and not actual_fraud:
            nb_fp += 1
            nb_fp_cost += 1
        elif not nb_pred and not actual_fraud:
            nb_tn += 1
        elif not nb_pred and actual_fraud:
            nb_fn += 1

    def calc(tp, fp, tn, fn, cost):
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        return {
            'precision': round(precision, 4),
            'recall': round(recall, 4),
            'f1': round(f1, 4),
            'fpr': round(fpr, 4),
            'fp_cost': cost,
            'tp': tp,
            'fp': fp,
            'tn': tn,
            'fn': fn
        }
        
    return {
        'ring_sentinel': calc(rs_tp, rs_fp, rs_tn, rs_fn, rs_fp_cost),
        'naive_baseline': calc(nb_tp, nb_fp, nb_tn, nb_fn, nb_fp_cost)
    }

def compute_metrics(clusters: list[dict], orders: list[dict], naive_threshold: float = 500.0) -> dict:
    flagged_customers = set()
    for c in clusters:
        if float(c.get('risk_score', 0) or 0) >= 0.5:
            flagged_customers.update(c.get('member_customer_ids', []))
            
    # Sort orders chronologically to cleanly separate the held-out test set
    sorted_orders = sorted(orders, key=lambda x: str(x.get('order_timestamp', '')))
    split_idx = int(len(sorted_orders) * 0.8)
    
    training_orders = sorted_orders[:split_idx]
    test_orders = sorted_orders[split_idx:]
    
    # Evaluate strictly on held-out test set (last 20%) as required by specification
    test_metrics = evaluate_dataset(test_orders, flagged_customers, naive_threshold)
    all_metrics = evaluate_dataset(sorted_orders, flagged_customers, naive_threshold)
    
    return {
        'ring_sentinel': test_metrics['ring_sentinel'],
        'naive_baseline': test_metrics['naive_baseline'],
        'test_set_size': len(test_orders),
        'training_set_size': len(training_orders),
        'total_orders': len(sorted_orders),
        'overall': all_metrics
    }
