import sys
import os
from database.database import get_db, SessionLocal
from database import models

def check_data():
    db = SessionLocal()
    try:
        n_customers = db.query(models.Customer).count()
        n_transactions = db.query(models.Transaction).count()
        n_rfm = db.query(models.RFMScore).count()
        n_churn = db.query(models.ChurnPrediction).count()
        n_clv = db.query(models.CLVPrediction).count()

        print(f"Customers: {n_customers}")
        print(f"Transactions: {n_transactions}")
        print(f"RFM Scores: {n_rfm}")
        print(f"Churn Predictions: {n_churn}")
        print(f"CLV Predictions: {n_clv}")

        if n_customers > 0:
            c = db.query(models.Customer).first()
            print(f"Sample Customer: {c.customer_id}, Reg Date: {c.registration_date}")

        if n_transactions > 0:
            t = db.query(models.Transaction).first()
            print(f"Sample Transaction: {t.transaction_id}, Date: {t.transaction_date}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
