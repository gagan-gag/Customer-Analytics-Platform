"""
Initialization script - Generate data and train models
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.generate_data import SyntheticDataGenerator
from database.database import init_db, SessionLocal
from database import models
from services.customer_service import CustomerService
from services.analytics_service import AnalyticsService
import pandas as pd
from config import settings


def main():
    print("=" * 60)
    print("Customer Analytics Platform - Initialization")
    print("=" * 60)
    
    # Step 1: Initialize database
    print("\n[1/5] Initializing database...")
    init_db()
    print("[OK] Database initialized")
    
    # Step 2: Generate synthetic data
    print("\n[2/5] Generating synthetic customer data...")
    generator = SyntheticDataGenerator(
        num_customers=settings.SYNTHETIC_CUSTOMERS,
        date_range_days=settings.SYNTHETIC_DATE_RANGE_DAYS
    )
    customers_df, transactions_df = generator.generate_data()
    print(f"[OK] Generated {len(customers_df)} customers and {len(transactions_df)} transactions")
    
    # Step 3: Import data into database
    print("\n[3/5] Importing data into database...")
    db = SessionLocal()
    try:
        customer_service = CustomerService(db)
        
        # Import customers
        print("  - Importing customers...")
        for _, row in customers_df.iterrows():
            customer = models.Customer(
                customer_id=row['customer_id'],
                name=row['name'],
                email=row['email'],
                phone=row['phone'],
                country=row['country'],
                city=row['city'],
                registration_date=row['registration_date']
            )
            db.add(customer)
        db.commit()
        print(f"  [OK] Imported {len(customers_df)} customers")
        
        # Import transactions
        print("  - Importing transactions...")
        for _, row in transactions_df.iterrows():
            customer = db.query(models.Customer).filter(
                models.Customer.customer_id == row['customer_id']
            ).first()
            
            if customer:
                transaction = models.Transaction(
                    transaction_id=row['transaction_id'],
                    customer_id=customer.id,
                    transaction_date=row['transaction_date'],
                    amount=row['amount'],
                    quantity=row['quantity'],
                    product_category=row['product_category'],
                    product_name=row['product_name']
                )
                db.add(transaction)
        
        db.commit()
        print(f"  [OK] Imported {len(transactions_df)} transactions")
        
    finally:
        db.close()
    
    # Step 4: Train ML models
    print("\n[4/5] Training ML models...")
    db = SessionLocal()
    try:
        analytics_service = AnalyticsService(db)
        
        # Train RFM
        print("  - Training RFM segmentation model...")
        rfm_result = analytics_service.train_rfm_model()
        print(f"  [OK] RFM model trained: {rfm_result.get('customers_segmented', 0)} customers segmented")
        
        # Train Churn Prediction
        print("  - Training churn prediction model...")
        churn_result = analytics_service.train_churn_model()
        print(f"  [OK] Churn model trained")
        print(f"    - Accuracy: {churn_result.get('accuracy', 0):.3f}")
        print(f"    - F1 Score: {churn_result.get('f1_score', 0):.3f}")
        
        # Train CLV Estimation
        print("  - Training CLV estimation model...")
        clv_result = analytics_service.train_clv_model()
        print(f"  [OK] CLV model trained")
        print(f"    - RMSE: {clv_result.get('rmse', 0):.2f}")
        print(f"    - R² Score: {clv_result.get('r2_score', 0):.3f}")
        
    finally:
        db.close()
    
    # Step 5: Summary
    print("\n[5/5] Initialization complete!")
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    print(f"[OK] Database: Initialized")
    print(f"[OK] Customers: {len(customers_df)}")
    print(f"[OK] Transactions: {len(transactions_df)}")
    print(f"[OK] ML Models: RFM, Churn, CLV trained")
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Start the backend server:")
    print("   cd backend")
    print("   python app.py")
    print("\n2. Start the frontend (in a new terminal):")
    print("   cd frontend")
    print("   npm install")
    print("   npm run dev")
    print("\n3. Access the application:")
    print("   Frontend: http://localhost:5173")
    print("   API Docs: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    main()
