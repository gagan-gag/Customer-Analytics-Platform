"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# Customer Schemas
class CustomerBase(BaseModel):
    customer_id: str
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    registration_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionBase(BaseModel):
    transaction_id: str
    transaction_date: datetime
    amount: float = Field(gt=0)
    quantity: int = Field(default=1, gt=0)
    product_category: Optional[str] = None
    product_name: Optional[str] = None


class TransactionCreate(TransactionBase):
    customer_id: str


class TransactionResponse(TransactionBase):
    id: int
    customer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# RFM Schemas
class RFMScoreResponse(BaseModel):
    customer_id: int
    recency: int
    frequency: int
    monetary: float
    recency_score: int
    frequency_score: int
    monetary_score: int
    rfm_score: str
    segment: str
    calculated_at: datetime
    
    class Config:
        from_attributes = True


class RFMSegmentSummary(BaseModel):
    segment: str
    customer_count: int
    avg_recency: float
    avg_frequency: float
    avg_monetary: float
    total_value: float
    percentage: float


# Churn Schemas
class ChurnPredictionResponse(BaseModel):
    customer_id: int
    customer_str_id: Optional[str] = None  # The string customer_id from Customer table
    customer_name: Optional[str] = None
    churn_probability: float
    churn_risk: str
    is_churned: bool
    risk_factors: Optional[str] = None
    predicted_at: datetime
    
    class Config:
        from_attributes = True


class ChurnAnalysisSummary(BaseModel):
    total_customers: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    avg_churn_probability: float


# CLV Schemas
class CLVPredictionResponse(BaseModel):
    customer_id: int
    customer_str_id: Optional[str] = None  # The string customer_id from Customer table
    customer_name: Optional[str] = None
    predicted_clv: float
    clv_segment: str
    historical_value: float
    avg_order_value: float
    purchase_frequency: float
    predicted_at: datetime
    
    class Config:
        from_attributes = True


class CLVAnalysisSummary(BaseModel):
    total_customers: int
    total_predicted_clv: float
    avg_clv: float
    high_value_count: int
    medium_value_count: int
    low_value_count: int


# Dashboard Schemas
class DashboardMetrics(BaseModel):
    total_customers: int
    total_revenue: float
    avg_order_value: float
    total_transactions: int
    active_customers: int
    churn_rate: float
    avg_customer_lifetime_value: float
    
    # Segment distribution
    segment_distribution: List[dict]
    
    # Trends
    revenue_trend: List[dict]
    customer_acquisition_trend: List[dict]


# Analytics Schemas
class CustomerDetailedAnalytics(BaseModel):
    customer: CustomerResponse
    rfm_score: Optional[RFMScoreResponse] = None
    churn_prediction: Optional[ChurnPredictionResponse] = None
    clv_prediction: Optional[CLVPredictionResponse] = None
    transactions: List[TransactionResponse]
    total_spent: float
    transaction_count: int
    avg_transaction_value: float
    last_purchase_date: Optional[datetime] = None


# Recommendation Schemas
class RetentionStrategy(BaseModel):
    segment: str
    strategy: str
    priority: str
    actions: List[str]
    expected_impact: str


class RecommendationResponse(BaseModel):
    customer_id: int
    customer_name: str
    segment: str
    churn_risk: str
    clv_segment: str
    recommended_actions: List[str]
    priority: str


# Upload Schemas
class UploadResponse(BaseModel):
    success: bool
    message: str
    customers_imported: int
    transactions_imported: int
    errors: Optional[List[str]] = None


# Model Performance Schemas
class ModelPerformanceResponse(BaseModel):
    model_name: str
    model_version: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    rmse: Optional[float] = None
    mae: Optional[float] = None
    training_samples: int
    trained_at: datetime
    
    class Config:
        from_attributes = True
