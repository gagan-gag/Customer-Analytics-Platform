"""
Configuration settings for the Customer Analytics Platform
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Customer Segmentation & Retention Analytics"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # API
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/customers.db"
    
    # ML Models
    MODEL_PATH: str = "./models/saved_models"
    RANDOM_STATE: int = 42
    
    # RFM Segmentation
    RFM_SEGMENTS: int = 5
    RFM_LABELS: dict = {
        "Champions": {"R": [4, 5], "F": [4, 5], "M": [4, 5]},
        "Loyal Customers": {"R": [3, 5], "F": [3, 5], "M": [3, 5]},
        "Potential Loyalists": {"R": [3, 5], "F": [1, 3], "M": [1, 3]},
        "New Customers": {"R": [4, 5], "F": [1, 1], "M": [1, 1]},
        "Promising": {"R": [3, 4], "F": [1, 1], "M": [1, 1]},
        "Need Attention": {"R": [3, 4], "F": [3, 4], "M": [3, 4]},
        "About to Sleep": {"R": [2, 3], "F": [1, 3], "M": [1, 3]},
        "At Risk": {"R": [1, 2], "F": [3, 5], "M": [3, 5]},
        "Cannot Lose Them": {"R": [1, 2], "F": [4, 5], "M": [4, 5]},
        "Hibernating": {"R": [1, 2], "F": [1, 2], "M": [1, 2]},
        "Lost": {"R": [1, 1], "F": [1, 2], "M": [1, 2]}
    }
    
    # Churn Prediction
    CHURN_THRESHOLD: float = 0.5
    CHURN_FEATURES: list = [
        "recency", "frequency", "monetary", "avg_order_value",
        "days_since_last_purchase", "purchase_frequency",
        "total_transactions", "customer_age_days"
    ]
    
    # CLV Estimation
    CLV_DISCOUNT_RATE: float = 0.1
    CLV_PREDICTION_MONTHS: int = 12
    
    # Data Generation
    SYNTHETIC_CUSTOMERS: int = 1000
    SYNTHETIC_DATE_RANGE_DAYS: int = 730  # 2 years
    
    # Export
    EXPORT_PATH: str = "./exports"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
