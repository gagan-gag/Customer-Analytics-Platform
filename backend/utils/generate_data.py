"""
Synthetic customer data generator for demo purposes
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
import sys
import os

# Add parent directory to path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings


class SyntheticDataGenerator:
    """Generate realistic customer and transaction data"""
    
    def __init__(self, num_customers=1000, date_range_days=730):
        self.num_customers = num_customers
        self.date_range_days = date_range_days
        self.start_date = datetime.now() - timedelta(days=date_range_days)
        self.end_date = datetime.now()
        
        # Sample data
        self.first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
            "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
            "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
            "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
            "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
            "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
        ]
        
        self.countries = [
            "United States", "United Kingdom", "Canada", "Australia", "Germany",
            "France", "Spain", "Italy", "Netherlands", "Sweden", "Norway", "Denmark",
            "India", "Singapore", "Japan", "South Korea", "Brazil", "Mexico"
        ]
        
        self.cities = {
            "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
            "United Kingdom": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"],
            "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
            "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide"],
            "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne"],
            "France": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"],
            "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
        }
        
        self.product_categories = [
            "Electronics", "Clothing", "Home & Garden", "Sports & Outdoors",
            "Books", "Toys & Games", "Health & Beauty", "Food & Beverages",
            "Automotive", "Office Supplies"
        ]
        
        self.products = {
            "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Camera", "Smart Watch"],
            "Clothing": ["T-Shirt", "Jeans", "Dress", "Jacket", "Shoes", "Accessories"],
            "Home & Garden": ["Furniture", "Decor", "Kitchen Appliances", "Bedding", "Tools"],
            "Sports & Outdoors": ["Fitness Equipment", "Camping Gear", "Sportswear", "Bicycle"],
            "Books": ["Fiction", "Non-Fiction", "Educational", "Comics", "Magazines"],
            "Toys & Games": ["Board Games", "Action Figures", "Puzzles", "Video Games"],
            "Health & Beauty": ["Skincare", "Makeup", "Supplements", "Personal Care"],
            "Food & Beverages": ["Snacks", "Beverages", "Gourmet Food", "Organic Products"],
            "Automotive": ["Car Accessories", "Tools", "Cleaning Supplies", "Parts"],
            "Office Supplies": ["Stationery", "Desk Accessories", "Electronics", "Furniture"]
        }
    
    def generate_customer_id(self):
        """Generate unique customer ID"""
        return 'CUST' + ''.join(random.choices(string.digits, k=8))
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        return 'TXN' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    def generate_customers(self):
        """Generate customer data"""
        customers = []
        
        for i in range(self.num_customers):
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            country = random.choice(self.countries)
            city = random.choice(self.cities.get(country, ["Unknown"]))
            
            # Registration date - weighted towards more recent
            days_ago = int(np.random.exponential(scale=self.date_range_days / 3))
            days_ago = min(days_ago, self.date_range_days)
            registration_date = self.end_date - timedelta(days=days_ago)
            
            customer = {
                'customer_id': self.generate_customer_id(),
                'name': f"{first_name} {last_name}",
                'email': f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@example.com",
                'phone': f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                'country': country,
                'city': city,
                'registration_date': registration_date
            }
            customers.append(customer)
        
        return pd.DataFrame(customers)
    
    def generate_transactions(self, customers_df):
        """Generate transaction data with realistic patterns"""
        transactions = []
        
        for _, customer in customers_df.iterrows():
            # Determine customer behavior pattern
            customer_type = random.choices(
                ['champion', 'loyal', 'occasional', 'one_time', 'churned'],
                weights=[0.15, 0.25, 0.35, 0.15, 0.10]
            )[0]
            
            # Set transaction patterns based on customer type
            if customer_type == 'champion':
                num_transactions = random.randint(20, 50)
                avg_amount = random.uniform(100, 500)
                recency_days = random.randint(1, 30)
            elif customer_type == 'loyal':
                num_transactions = random.randint(10, 25)
                avg_amount = random.uniform(75, 300)
                recency_days = random.randint(1, 60)
            elif customer_type == 'occasional':
                num_transactions = random.randint(3, 10)
                avg_amount = random.uniform(50, 200)
                recency_days = random.randint(30, 180)
            elif customer_type == 'one_time':
                num_transactions = 1
                avg_amount = random.uniform(30, 150)
                recency_days = random.randint(180, 600)
            else:  # churned
                num_transactions = random.randint(2, 8)
                avg_amount = random.uniform(40, 180)
                recency_days = random.randint(365, self.date_range_days)
            
            # Generate transactions
            registration_date = customer['registration_date']
            max_transaction_date = self.end_date - timedelta(days=recency_days)
            
            for _ in range(num_transactions):
                # Transaction date between registration and max date
                days_range = (max_transaction_date - registration_date).days
                if days_range <= 0:
                    continue
                
                transaction_date = registration_date + timedelta(
                    days=random.randint(0, days_range)
                )
                
                # Amount with some variation
                amount = max(10, np.random.normal(avg_amount, avg_amount * 0.3))
                
                # Product details
                category = random.choice(self.product_categories)
                product = random.choice(self.products[category])
                
                transaction = {
                    'transaction_id': self.generate_transaction_id(),
                    'customer_id': customer['customer_id'],
                    'transaction_date': transaction_date,
                    'amount': round(amount, 2),
                    'quantity': random.randint(1, 5),
                    'product_category': category,
                    'product_name': product
                }
                transactions.append(transaction)
        
        return pd.DataFrame(transactions)
    
    def generate_data(self):
        """Generate complete dataset"""
        print(f"Generating {self.num_customers} customers...")
        customers_df = self.generate_customers()
        
        print("Generating transactions...")
        transactions_df = self.generate_transactions(customers_df)
        
        print(f"Generated {len(customers_df)} customers and {len(transactions_df)} transactions")
        
        return customers_df, transactions_df
    
    def save_to_csv(self, output_dir="./data"):
        """Save generated data to CSV files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        customers_df, transactions_df = self.generate_data()
        
        customers_file = os.path.join(output_dir, "customers.csv")
        transactions_file = os.path.join(output_dir, "transactions.csv")
        
        customers_df.to_csv(customers_file, index=False)
        transactions_df.to_csv(transactions_file, index=False)
        
        print(f"\nData saved to:")
        print(f"  - {customers_file}")
        print(f"  - {transactions_file}")
        
        return customers_df, transactions_df


if __name__ == "__main__":
    # Generate synthetic data
    generator = SyntheticDataGenerator(
        num_customers=settings.SYNTHETIC_CUSTOMERS,
        date_range_days=settings.SYNTHETIC_DATE_RANGE_DAYS
    )
    generator.save_to_csv()
