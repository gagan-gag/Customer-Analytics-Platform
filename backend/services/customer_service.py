"""
Customer Service - Business logic for customer management
"""
from sqlalchemy.orm import Session
from database import models, schemas
from typing import List, Optional
import pandas as pd
from datetime import datetime
import os


class CustomerService:
    """Service for customer-related operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_customers(self, skip: int = 0, limit: int = 100) -> List[models.Customer]:
        """Get list of customers"""
        return self.db.query(models.Customer).offset(skip).limit(limit).all()
    
    def get_customer_by_id(self, customer_id: int) -> Optional[models.Customer]:
        """Get customer by database ID"""
        return self.db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    
    def get_customer_by_customer_id(self, customer_id: str) -> Optional[models.Customer]:
        """Get customer by customer_id string"""
        return self.db.query(models.Customer).filter(
            models.Customer.customer_id == customer_id
        ).first()
    
    def create_customer(self, customer_data: schemas.CustomerCreate) -> models.Customer:
        """Create a new customer"""
        db_customer = models.Customer(**customer_data.dict())
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer
    
    def get_customer_transactions(self, customer_id: str) -> List[models.Transaction]:
        """Get all transactions for a customer"""
        customer = self.get_customer_by_customer_id(customer_id)
        if not customer:
            return []
        return customer.transactions
    
    def get_customer_analytics(self, customer_id: str) -> schemas.CustomerDetailedAnalytics:
        """Get detailed analytics for a customer"""
        customer = self.get_customer_by_customer_id(customer_id)
        if not customer:
            return None
        
        transactions = customer.transactions
        total_spent = sum(t.amount for t in transactions)
        transaction_count = len(transactions)
        avg_transaction = total_spent / transaction_count if transaction_count > 0 else 0
        last_purchase = max([t.transaction_date for t in transactions]) if transactions else None
        
        return schemas.CustomerDetailedAnalytics(
            customer=customer,
            rfm_score=customer.rfm_score,
            churn_prediction=customer.churn_prediction,
            clv_prediction=customer.clv_prediction,
            transactions=transactions,
            total_spent=total_spent,
            transaction_count=transaction_count,
            avg_transaction_value=avg_transaction,
            last_purchase_date=last_purchase
        )
    
    def _clean_value(self, value, default=None):
        """Clean NaN/None values from DataFrame cells"""
        if pd.isna(value) or value == '' or value == 'nan':
            return default
        return value
    
    def import_data(self, df: pd.DataFrame) -> schemas.UploadResponse:
        """
        Import customer and transaction data from DataFrame
        
        Expected columns for customers:
        - customer_id, name, email, phone, country, city, registration_date
        
        Expected columns for transactions:
        - transaction_id, customer_id, transaction_date, amount, quantity, 
          product_category, product_name
        """
        errors = []
        customers_imported = 0
        transactions_imported = 0
        
        # Normalize column names (strip whitespace, lowercase)
        df.columns = df.columns.str.strip().str.lower()
        
        try:
            # Detect data type based on columns
            customer_cols = ['customer_id', 'name', 'email']
            transaction_cols = ['transaction_id', 'customer_id', 'amount']
            
            is_customer_data = all(col in df.columns for col in customer_cols)
            is_transaction_data = all(col in df.columns for col in transaction_cols)
            
            if is_customer_data and not is_transaction_data:
                # Import customers
                for _, row in df.iterrows():
                    try:
                        cust_id = str(row['customer_id']).strip()
                        
                        # Check if customer already exists
                        existing = self.get_customer_by_customer_id(cust_id)
                        if existing:
                            continue
                        
                        customer = models.Customer(
                            customer_id=cust_id,
                            name=str(self._clean_value(row.get('name'), f"Customer {cust_id}")),
                            email=self._clean_value(row.get('email')),
                            phone=self._clean_value(row.get('phone')),
                            country=self._clean_value(row.get('country')),
                            city=self._clean_value(row.get('city')),
                            registration_date=pd.to_datetime(
                                self._clean_value(row.get('registration_date'), datetime.now())
                            )
                        )
                        self.db.add(customer)
                        customers_imported += 1
                    except Exception as e:
                        self.db.rollback()
                        errors.append(f"Error importing customer {row.get('customer_id')}: {str(e)}")
                
                self.db.commit()
            
            elif is_transaction_data:
                # Import transactions
                for _, row in df.iterrows():
                    try:
                        cust_id = str(row['customer_id']).strip()
                        txn_id = str(row['transaction_id']).strip()
                        
                        # Get or create customer
                        customer = self.get_customer_by_customer_id(cust_id)
                        if not customer:
                            # Create customer if doesn't exist
                            customer = models.Customer(
                                customer_id=cust_id,
                                name=str(self._clean_value(row.get('name'), f"Customer {cust_id}")),
                                email=self._clean_value(row.get('email')),
                                registration_date=datetime.now()
                            )
                            self.db.add(customer)
                            self.db.flush()
                            customers_imported += 1
                        
                        # Check if transaction already exists
                        existing_txn = self.db.query(models.Transaction).filter(
                            models.Transaction.transaction_id == txn_id
                        ).first()
                        
                        if existing_txn:
                            continue
                        
                        transaction = models.Transaction(
                            transaction_id=txn_id,
                            customer_id=customer.id,
                            transaction_date=pd.to_datetime(row['transaction_date']),
                            amount=float(row['amount']),
                            quantity=int(self._clean_value(row.get('quantity'), 1)),
                            product_category=self._clean_value(row.get('product_category')),
                            product_name=self._clean_value(row.get('product_name'))
                        )
                        self.db.add(transaction)
                        transactions_imported += 1
                    except Exception as e:
                        self.db.rollback()
                        errors.append(f"Error importing transaction {row.get('transaction_id')}: {str(e)}")
                
                self.db.commit()
            
            else:
                return schemas.UploadResponse(
                    success=False,
                    message="Unable to detect data format. Please ensure required columns are present.",
                    customers_imported=0,
                    transactions_imported=0,
                    errors=[f"Invalid data format. Found columns: {list(df.columns)}"]
                )
            
            return schemas.UploadResponse(
                success=True,
                message=f"Successfully imported {customers_imported} customers and {transactions_imported} transactions",
                customers_imported=customers_imported,
                transactions_imported=transactions_imported,
                errors=errors if errors else None
            )
        
        except Exception as e:
            self.db.rollback()
            return schemas.UploadResponse(
                success=False,
                message=f"Import failed: {str(e)}",
                customers_imported=customers_imported,
                transactions_imported=transactions_imported,
                errors=[str(e)]
            )
    
    def export_customers(self, format: str = "csv") -> str:
        """Export customers to file"""
        customers = self.get_customers(limit=10000)
        
        data = []
        for customer in customers:
            data.append({
                'customer_id': customer.customer_id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'country': customer.country,
                'city': customer.city,
                'registration_date': customer.registration_date
            })
        
        df = pd.DataFrame(data)
        
        os.makedirs("./exports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "excel":
            file_path = f"./exports/customers_{timestamp}.xlsx"
            df.to_excel(file_path, index=False)
        else:
            file_path = f"./exports/customers_{timestamp}.csv"
            df.to_csv(file_path, index=False)
        
        return file_path
