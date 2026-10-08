"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.database import Base


class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, index=True)
    phone = Column(String)
    country = Column(String)
    city = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    rfm_score = relationship("RFMScore", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    churn_prediction = relationship("ChurnPrediction", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    clv_prediction = relationship("CLVPrediction", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transaction(Base):
    """Transaction/Purchase model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    product_category = Column(String)
    product_name = Column(String)
    
    # Relationship
    customer = relationship("Customer", back_populates="transactions")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class RFMScore(Base):
    """RFM Segmentation scores"""
    __tablename__ = "rfm_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)
    
    # RFM Metrics
    recency = Column(Integer)  # Days since last purchase
    frequency = Column(Integer)  # Number of purchases
    monetary = Column(Float)  # Total spend
    
    # RFM Scores (1-5)
    recency_score = Column(Integer)
    frequency_score = Column(Integer)
    monetary_score = Column(Integer)
    rfm_score = Column(String)  # Combined score e.g., "555"
    
    # Segment
    segment = Column(String)  # e.g., "Champions", "At Risk"
    
    # Relationship
    customer = relationship("Customer", back_populates="rfm_score")
    
    calculated_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChurnPrediction(Base):
    """Churn prediction results"""
    __tablename__ = "churn_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)
    
    churn_probability = Column(Float)  # 0-1
    churn_risk = Column(String)  # Low, Medium, High
    is_churned = Column(Boolean, default=False)
    
    # Contributing factors
    risk_factors = Column(Text)  # JSON string of factors
    
    # Relationship
    customer = relationship("Customer", back_populates="churn_prediction")
    
    predicted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CLVPrediction(Base):
    """Customer Lifetime Value predictions"""
    __tablename__ = "clv_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)
    
    predicted_clv = Column(Float)
    clv_segment = Column(String)  # High, Medium, Low
    
    # Historical metrics
    historical_value = Column(Float)
    avg_order_value = Column(Float)
    purchase_frequency = Column(Float)
    
    # Relationship
    customer = relationship("Customer", back_populates="clv_prediction")
    
    predicted_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ModelMetadata(Base):
    """ML Model training metadata"""
    __tablename__ = "model_metadata"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False)  # churn, clv, rfm
    model_version = Column(String)
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    rmse = Column(Float)
    mae = Column(Float)
    
    # Training info
    training_samples = Column(Integer)
    features_used = Column(Text)  # JSON string
    hyperparameters = Column(Text)  # JSON string
    
    trained_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
