import pandas as pd
import numpy as np

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/transactions.csv"

# Historical information is available up to this date.
OBSERVATION_END = pd.Timestamp("2025-08-22")

# We predict customer value during the following period.
PREDICTION_END = pd.Timestamp("2026-02-18")


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("Loading transaction data...")

    df = pd.read_csv(DATA_PATH)

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"]
    )

    print(f"Transactions: {len(df)}")
    print(f"Customers: {df['customer_id'].nunique()}")

    print(
        f"Date range: "
        f"{df['transaction_date'].min().date()} "
        f"to "
        f"{df['transaction_date'].max().date()}"
    )

    return df


# ============================================================
# CREATE HISTORICAL CUSTOMER FEATURES
# ============================================================

def create_features(transactions):

    """
    Create customer features using ONLY transactions
    available on or before the observation date.
    """

    historical = transactions[
        transactions["transaction_date"] <= OBSERVATION_END
    ].copy()

    features = historical.groupby("customer_id").agg(

        last_purchase=("transaction_date", "max"),

        first_purchase=("transaction_date", "min"),

        total_transactions=("transaction_id", "count"),

        total_spent=("amount", "sum"),

        avg_order_value=("amount", "mean"),

        std_order_value=("amount", "std"),

        max_order_value=("amount", "max"),

        min_order_value=("amount", "min"),

        total_quantity=("quantity", "sum"),

        avg_quantity=("quantity", "mean"),

    ).reset_index()

    # Replace missing standard deviation
    # for customers with only one transaction.
    features["std_order_value"] = (
        features["std_order_value"]
        .fillna(0)
    )

    reference_date = OBSERVATION_END

    features["days_since_last_purchase"] = (
        reference_date - features["last_purchase"]
    ).dt.days

    features["customer_lifetime_days"] = (
        features["last_purchase"]
        - features["first_purchase"]
    ).dt.days + 1

    features["purchase_frequency"] = (
        features["total_transactions"]
        / features["customer_lifetime_days"]
    ).fillna(0)

    features["revenue_per_day"] = (
        features["total_spent"]
        / features["customer_lifetime_days"]
    ).fillna(0)

    return features


# ============================================================
# CREATE FUTURE CUSTOMER VALUE TARGET
# ============================================================

def create_future_target(transactions, customer_features):

    """
    Target = total amount spent by each customer
    during the future prediction period.

    This target is NOT included in the input features.
    """

    future = transactions[
        (transactions["transaction_date"] > OBSERVATION_END)
        & (transactions["transaction_date"] <= PREDICTION_END)
    ].copy()

    future_value = (
        future.groupby("customer_id")["amount"]
        .sum()
        .reset_index()
    )

    future_value.columns = [
        "customer_id",
        "future_customer_value"
    ]

    data = customer_features.merge(
        future_value,
        on="customer_id",
        how="left"
    )

    # Customers with no future purchase have future value = 0.
    data["future_customer_value"] = (
        data["future_customer_value"]
        .fillna(0)
    )

    return data


# ============================================================
# TRAIN AND EVALUATE CLV MODEL
# ============================================================

def train_model(data):

    feature_columns = [

        "total_transactions",

        "total_spent",

        "avg_order_value",

        "std_order_value",

        "max_order_value",

        "min_order_value",

        "total_quantity",

        "avg_quantity",

        "days_since_last_purchase",

        "customer_lifetime_days",

        "purchase_frequency",

        "revenue_per_day",

    ]

    target_column = "future_customer_value"

    X = data[feature_columns]

    y = data[target_column]

    print("\n========================================")
    print("CLV DATASET")
    print("========================================")

    print(
        f"Customers used: {len(data)}"
    )

    print(
        f"Customers with future purchases: "
        f"{(y > 0).sum()}"
    )

    print(
        f"Customers with zero future value: "
        f"{(y == 0).sum()}"
    )

    print(
        f"Average future customer value: "
        f"{y.mean():.2f}"
    )

    print(
        f"Maximum future customer value: "
        f"{y.max():.2f}"
    )

    # ========================================================
    # TRAIN / TEST SPLIT
    # ========================================================

    X_train, X_test, y_train, y_test = train_test_split(

        X,
        y,

        test_size=0.20,

        random_state=42
    )

    print("\n========================================")
    print("TRAIN / TEST SPLIT")
    print("========================================")

    print(
        f"Training customers: {len(X_train)}"
    )

    print(
        f"Testing customers:  {len(X_test)}"
    )

    # ========================================================
    # GRADIENT BOOSTING REGRESSOR
    # ========================================================

    print("\nTraining Gradient Boosting Regressor...")

    model = GradientBoostingRegressor(

        n_estimators=100,

        max_depth=5,

        learning_rate=0.1,

        min_samples_split=10,

        min_samples_leaf=5,

        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    # Prevent negative predicted customer value.
    predictions = np.maximum(
        predictions,
        0
    )

    # ========================================================
    # RESULTS
    # ========================================================

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    print("\n========================================")
    print("RESULTS")
    print("========================================")

    print(
        f"MAE  : {mae:.4f}"
    )

    print(
        f"RMSE : {rmse:.4f}"
    )

    print(
        f"R²   : {r2:.4f}"
    )

    # ========================================================
    # FEATURE IMPORTANCE
    # ========================================================

    print("\nFeature Importance:")

    importance = pd.DataFrame({

        "feature": feature_columns,

        "importance": model.feature_importances_

    }).sort_values(
        "importance",
        ascending=False
    )

    print(
        importance.to_string(
            index=False
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("============================================")
    print("FUTURE CUSTOMER VALUE PREDICTION EXPERIMENT")
    print("============================================")

    print(
        f"\nObservation period ends: "
        f"{OBSERVATION_END.date()}"
    )

    print(
        f"Future value period: "
        f"{(OBSERVATION_END + pd.Timedelta(days=1)).date()} "
        f"to "
        f"{PREDICTION_END.date()}"
    )

    print(
        "\nTarget: Future customer spending"
    )

    transactions = load_data()

    features = create_features(
        transactions
    )

    data = create_future_target(
        transactions,
        features
    )

    train_model(
        data
    )


if __name__ == "__main__":
    main()