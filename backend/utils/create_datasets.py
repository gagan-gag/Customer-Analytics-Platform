"""
Dataset Generator Script
Creates multiple ready-to-upload CSV datasets with different sizes,
customer profiles, and churn characteristics.

Run with:
    cd backend
    python utils/create_datasets.py
"""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "datasets")

# Indian names & cities
INDIAN_FIRST = [
    "Aarav","Aditi","Akash","Ananya","Arjun","Deepa","Devika","Gaurav",
    "Ishaan","Kavya","Kiran","Manish","Meera","Nidhi","Nikhil","Pooja",
    "Priya","Rahul","Raj","Riya","Rohit","Sanya","Siddharth","Sneha",
    "Suresh","Tanvi","Varun","Vikram","Vivek","Zoya"
]
INDIAN_LAST = [
    "Agarwal","Bhatia","Chauhan","Chopra","Desai","Gupta","Iyer","Jain",
    "Kapoor","Khanna","Kumar","Mehta","Mishra","Nair","Patel","Pillai",
    "Reddy","Sharma","Singh","Srivastava","Verma","Yadav"
]
INDIAN_CITIES = [
    "Mumbai","Delhi","Bangalore","Hyderabad","Chennai",
    "Kolkata","Pune","Ahmedabad","Jaipur","Surat",
    "Lucknow","Kanpur","Nagpur","Indore","Thane"
]

# Global names & cities
GLOBAL_FIRST = [
    "James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda",
    "William","Elizabeth","David","Barbara","Richard","Susan","Joseph","Jessica",
    "Thomas","Sarah","Charles","Karen","Christopher","Nancy","Daniel","Lisa",
    "Matthew","Betty","Anthony","Margaret","Mark","Sandra","Emily","Ashley"
]
GLOBAL_LAST = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
    "Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson",
    "Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson",
    "White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson","Walker"
]
GLOBAL_CITIES = {
    "United States": ["New York","Los Angeles","Chicago","Houston","Phoenix"],
    "United Kingdom": ["London","Manchester","Birmingham","Leeds","Glasgow"],
    "Canada": ["Toronto","Vancouver","Montreal","Calgary","Ottawa"],
    "Australia": ["Sydney","Melbourne","Brisbane","Perth","Adelaide"],
    "Germany": ["Berlin","Munich","Hamburg","Frankfurt","Cologne"],
    "France": ["Paris","Lyon","Marseille","Toulouse","Nice"],
    "Japan": ["Tokyo","Osaka","Kyoto","Hiroshima","Yokohama"],
    "Brazil": ["Sao Paulo","Rio de Janeiro","Brasilia","Salvador","Fortaleza"],
    "Singapore": ["Singapore"],
    "India": INDIAN_CITIES,
}

PRODUCT_CATEGORIES = [
    "Electronics","Clothing","Home & Garden","Sports & Outdoors",
    "Books","Toys & Games","Health & Beauty","Food & Beverages",
    "Automotive","Office Supplies"
]
PRODUCTS = {
    "Electronics": ["Laptop","Smartphone","Tablet","Headphones","Camera","Smart Watch","Speaker"],
    "Clothing": ["T-Shirt","Jeans","Dress","Jacket","Shoes","Accessories","Kurta"],
    "Home & Garden": ["Furniture","Decor","Kitchen Appliances","Bedding","Tools","Mixer"],
    "Sports & Outdoors": ["Fitness Equipment","Camping Gear","Sportswear","Bicycle","Yoga Mat"],
    "Books": ["Fiction","Non-Fiction","Educational","Comics","Magazines","Textbook"],
    "Toys & Games": ["Board Games","Action Figures","Puzzles","Video Games","LEGO"],
    "Health & Beauty": ["Skincare","Makeup","Supplements","Personal Care","Ayurveda"],
    "Food & Beverages": ["Snacks","Beverages","Gourmet Food","Organic Products","Masala"],
    "Automotive": ["Car Accessories","Tools","Cleaning Supplies","Parts","Helmet"],
    "Office Supplies": ["Stationery","Desk Accessories","Electronics","Furniture","Printer"],
}


def cust_id():
    return "CUST" + "".join(random.choices(string.digits, k=8))


def txn_id():
    return "TXN" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generate_customers(n, first_names, last_names, countries, cities_map, date_range_days=730):
    end = datetime.now()
    rows = []
    for _ in range(n):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        country = random.choice(countries)
        city_list = cities_map.get(country, ["Unknown"])
        city = random.choice(city_list if isinstance(city_list, list) else [city_list])
        days_ago = min(int(np.random.exponential(date_range_days / 3)), date_range_days)
        reg_date = end - timedelta(days=days_ago)
        rows.append({
            "customer_id": cust_id(),
            "name": fn + " " + ln,
            "email": fn.lower() + "." + ln.lower() + str(random.randint(1,999)) + "@example.com",
            "phone": "+91-" + str(random.randint(7000000000,9999999999)) if "India" in countries
                     else "+1-" + str(random.randint(100,999)) + "-" + str(random.randint(1000,9999)),
            "country": country,
            "city": city,
            "registration_date": reg_date.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return pd.DataFrame(rows)


def generate_transactions(customers_df, profile, date_range_days=730):
    end = datetime.now()
    weights = [
        profile["champion_w"], profile["loyal_w"],
        profile["occasional_w"], profile["one_time_w"], profile["churned_w"]
    ]
    rows = []
    for _, cust in customers_df.iterrows():
        ctype = random.choices(
            ["champion","loyal","occasional","one_time","churned"],
            weights=weights
        )[0]
        if ctype == "champion":
            n_txn = random.randint(*profile.get("champion_txn", (20, 50)))
            avg_amt = random.uniform(*profile.get("champion_amt", (100, 500)))
            rec = random.randint(1, 30)
        elif ctype == "loyal":
            n_txn = random.randint(*profile.get("loyal_txn", (10, 25)))
            avg_amt = random.uniform(*profile.get("loyal_amt", (75, 300)))
            rec = random.randint(1, 60)
        elif ctype == "occasional":
            n_txn = random.randint(*profile.get("occasional_txn", (3, 10)))
            avg_amt = random.uniform(*profile.get("occasional_amt", (50, 200)))
            rec = random.randint(30, 180)
        elif ctype == "one_time":
            n_txn = 1
            avg_amt = random.uniform(30, 150)
            rec = random.randint(180, 600)
        else:  # churned
            n_txn = random.randint(*profile.get("churned_txn", (2, 8)))
            avg_amt = random.uniform(*profile.get("churned_amt", (40, 180)))
            rec = random.randint(365, date_range_days)

        reg = datetime.strptime(cust["registration_date"], "%Y-%m-%d %H:%M:%S")
        max_date = end - timedelta(days=rec)
        for _ in range(n_txn):
            days_range = (max_date - reg).days
            if days_range <= 0:
                continue
            txn_date = reg + timedelta(days=random.randint(0, days_range))
            amount = max(10.0, float(np.random.normal(avg_amt, avg_amt * 0.3)))
            cat = random.choice(PRODUCT_CATEGORIES)
            rows.append({
                "transaction_id": txn_id(),
                "customer_id": cust["customer_id"],
                "transaction_date": txn_date.strftime("%Y-%m-%d %H:%M:%S"),
                "amount": round(amount, 2),
                "quantity": random.randint(1, 5),
                "product_category": cat,
                "product_name": random.choice(PRODUCTS[cat]),
            })
    return pd.DataFrame(rows)


def save(name, customers_df, transactions_df):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cf = os.path.join(OUTPUT_DIR, name + "_customers.csv")
    tf = os.path.join(OUTPUT_DIR, name + "_transactions.csv")
    customers_df.to_csv(cf, index=False)
    transactions_df.to_csv(tf, index=False)
    print("  [OK] " + name + ": " + str(len(customers_df)) + " customers | " + str(len(transactions_df)) + " transactions")
    print("       -> " + cf)
    print("       -> " + tf)


# Dataset definitions
DATASETS = [
    # 1. Small - Indian e-commerce (500 customers, high churn)
    dict(
        name="indian_ecommerce_small",
        description="Indian e-commerce, 500 customers, high churn",
        n=500,
        first_names=INDIAN_FIRST, last_names=INDIAN_LAST,
        countries=["India"], cities_map={"India": INDIAN_CITIES},
        date_range_days=365,
        profile=dict(
            champion_w=0.08, loyal_w=0.17, occasional_w=0.30,
            one_time_w=0.20, churned_w=0.25,
            champion_txn=(10,30), champion_amt=(500,3000),
            loyal_txn=(5,15), loyal_amt=(300,1500),
            occasional_txn=(2,8), occasional_amt=(200,800),
            churned_txn=(1,5), churned_amt=(100,500),
        )
    ),
    # 2. Medium - Global retail (1500 customers, balanced)
    dict(
        name="global_retail_medium",
        description="Global retail, 1500 customers, balanced profile",
        n=1500,
        first_names=GLOBAL_FIRST, last_names=GLOBAL_LAST,
        countries=list(GLOBAL_CITIES.keys()), cities_map=GLOBAL_CITIES,
        date_range_days=730,
        profile=dict(
            champion_w=0.15, loyal_w=0.25, occasional_w=0.35,
            one_time_w=0.15, churned_w=0.10,
        )
    ),
    # 3. Large - SaaS subscriptions (3000 customers, very loyal)
    dict(
        name="saas_subscriptions_large",
        description="SaaS/subscription business, 3000 customers, very loyal",
        n=3000,
        first_names=GLOBAL_FIRST, last_names=GLOBAL_LAST,
        countries=["United States","United Kingdom","Canada","Australia","Germany","Singapore"],
        cities_map=GLOBAL_CITIES,
        date_range_days=1095,
        profile=dict(
            champion_w=0.25, loyal_w=0.40, occasional_w=0.20,
            one_time_w=0.08, churned_w=0.07,
            champion_txn=(30,80), champion_amt=(200,800),
            loyal_txn=(15,35), loyal_amt=(100,400),
            occasional_txn=(5,15), occasional_amt=(80,300),
            churned_txn=(2,10), churned_amt=(50,200),
        )
    ),
    # 4. High-churn scenario (1000 customers, 45% churn rate)
    dict(
        name="high_churn_scenario",
        description="High-churn business, 1000 customers, 45% churn",
        n=1000,
        first_names=GLOBAL_FIRST + INDIAN_FIRST,
        last_names=GLOBAL_LAST + INDIAN_LAST,
        countries=list(GLOBAL_CITIES.keys()), cities_map=GLOBAL_CITIES,
        date_range_days=730,
        profile=dict(
            champion_w=0.05, loyal_w=0.10, occasional_w=0.20,
            one_time_w=0.20, churned_w=0.45,
            churned_txn=(1,5), churned_amt=(30,150),
        )
    ),
    # 5. Luxury premium (800 customers, very high spend)
    dict(
        name="luxury_premium",
        description="Luxury retail, 800 high-value customers",
        n=800,
        first_names=GLOBAL_FIRST, last_names=GLOBAL_LAST,
        countries=["United States","United Kingdom","Germany","France","Japan","Singapore"],
        cities_map=GLOBAL_CITIES,
        date_range_days=1095,
        profile=dict(
            champion_w=0.30, loyal_w=0.40, occasional_w=0.20,
            one_time_w=0.07, churned_w=0.03,
            champion_txn=(20,60), champion_amt=(2000,10000),
            loyal_txn=(10,25), loyal_amt=(1000,5000),
            occasional_txn=(3,10), occasional_amt=(500,2500),
            churned_txn=(1,4), churned_amt=(300,1000),
        )
    ),
]


def main():
    print("=" * 60)
    print("  Multi-Dataset Generator")
    print("  Output directory: " + OUTPUT_DIR)
    print("=" * 60)
    random.seed(42)
    np.random.seed(42)

    for ds in DATASETS:
        print("\n[>] Generating: [" + ds["name"] + "]")
        print("    " + ds["description"])
        customers_df = generate_customers(
            n=ds["n"],
            first_names=ds["first_names"],
            last_names=ds["last_names"],
            countries=ds["countries"],
            cities_map=ds["cities_map"],
            date_range_days=ds["date_range_days"],
        )
        transactions_df = generate_transactions(
            customers_df,
            profile=ds["profile"],
            date_range_days=ds["date_range_days"],
        )
        save(ds["name"], customers_df, transactions_df)

    print("\n" + "=" * 60)
    print("  All datasets created successfully!")
    print("  Find them in: " + OUTPUT_DIR)
    print("=" * 60)
    print("\n[*] How to use:")
    print("  1. Open the app -> Customers page")
    print("  2. If needed, click 'Clear All Data' first")
    print("  3. Click 'Upload Data', select a *_customers.csv file")
    print("  4. Then upload the matching *_transactions.csv file")
    print("  5. Go to each analysis page and click 'Retrain Model'")


if __name__ == "__main__":
    main()
