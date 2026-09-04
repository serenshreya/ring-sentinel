from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

class OrderResponse(BaseModel):
    order_id: int
    customer_id: str
    device_id: str
    ip_address: str
    delivery_address: str
    refund_bank_account: str
    amount: float
    order_timestamp: datetime
    is_fraud_label: bool

class ClusterResponse(BaseModel):
    cluster_id: int
    member_customer_ids: List[str]
    risk_score: Optional[float] = None
    status: Optional[str] = 'pending'
    explanation_text: Optional[str] = None

class DetectRequest(BaseModel):
    pass

class ScoreRequest(BaseModel):
    pass

class ClusterUpdateRequest(BaseModel):
    status: Literal['flagged', 'cleared']

class MetricsResponse(BaseModel):
    precision: float
    recall: float
    f1: float
    fpr: float
    fp_cost: int
    tp: Optional[int] = None
    fp: Optional[int] = None
    tn: Optional[int] = None
    fn: Optional[int] = None

class CombinedMetricsResponse(BaseModel):
    ring_sentinel: MetricsResponse
    naive_baseline: MetricsResponse
    test_set_size: Optional[int] = None
    training_set_size: Optional[int] = None
    total_orders: Optional[int] = None
    overall: Optional[dict] = None

class ExplanationResponse(BaseModel):
    cluster_id: int
    explanation_text: str
