import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/transactions.csv"

# We have data until 2026-02-18.
# Therefore, 2025-08-22 gives us a complete 180-day future window.
OBSERVATION_END = pd.Timestamp("2025-08-22")
PREDICTION_END = pd.Timestamp("2026-02-18")

CHURN_DAYS = 180


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
# CREATE CUSTOMER FEATURES
# ============================================================

def create_features(transactions):

    """
    Create customer features using only transactions
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

        total_quantity=("quantity", "sum"),

    ).reset_index()

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
# CREATE 180-DAY CHURN LABEL
# ============================================================

def create_future_labels(transactions, customer_features):

    """
    Churn definition:

    A customer is considered churned if they make
    NO purchase during the following 180 days.
    """

    future = transactions[
        (transactions["transaction_date"] > OBSERVATION_END)
        & (transactions["transaction_date"] <= PREDICTION_END)
    ].copy()

    future_activity = (
        future.groupby("customer_id")["transaction_date"]
        .max()
        .reset_index()
    )

    future_activity.columns = [
        "customer_id",
        "future_last_purchase"
    ]

    labels = customer_features[
        ["customer_id"]
    ].merge(
        future_activity,
        on="customer_id",
        how="left"
    )

    labels["is_churned"] = (
        labels["future_last_purchase"].isna()
    ).astype(int)

    return labels[
        ["customer_id", "is_churned"]
    ]


# ============================================================
# TRAIN AND EVALUATE MODEL
# ============================================================

def train_model(features, labels):

    data = features.merge(
        labels,
        on="customer_id",
        how="inner"
    )

    feature_columns = [

        "total_transactions",

        "total_spent",

        "avg_order_value",

        "total_quantity",

        "days_since_last_purchase",

        "customer_lifetime_days",

        "purchase_frequency",

        "revenue_per_day",

    ]

    print("\n========================================")
    print("CHURN DATASET")
    print("========================================")

    print(
        f"Customers used: {len(data)}"
    )

    print(
        f"Churned: {data['is_churned'].sum()}"
    )

    print(
        f"Not churned: "
        f"{(data['is_churned'] == 0).sum()}"
    )

    print("\nChurn percentage:")

    print(
        f"{data['is_churned'].mean() * 100:.2f}%"
    )

    # ========================================================
    # STRATIFIED TRAIN / TEST SPLIT
    # ========================================================

    train_data, test_data = train_test_split(

        data,

        test_size=0.20,

        random_state=42,

        stratify=data["is_churned"]
    )

    X_train = train_data[
        feature_columns
    ]

    y_train = train_data[
        "is_churned"
    ]

    X_test = test_data[
        feature_columns
    ]

    y_test = test_data[
        "is_churned"
    ]

    print("\n========================================")
    print("TRAIN / TEST SPLIT")
    print("========================================")

    print(
        f"Training customers: {len(train_data)}"
    )

    print(
        f"Testing customers:  {len(test_data)}"
    )

    print(
        f"Training churned: {y_train.sum()}"
    )

    print(
        f"Testing churned: {y_test.sum()}"
    )

    print(
        f"Training non-churned: "
        f"{(y_train == 0).sum()}"
    )

    print(
        f"Testing non-churned: "
        f"{(y_test == 0).sum()}"
    )

    # ========================================================
    # RANDOM FOREST
    # ========================================================

    print("\nTraining Random Forest...")

    model = RandomForestClassifier(

        n_estimators=100,

        max_depth=10,

        min_samples_split=10,

        min_samples_leaf=5,

        random_state=42,

        n_jobs=-1,

        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    # ========================================================
    # RESULTS
    # ========================================================

    print("\n========================================")
    print("RESULTS")
    print("========================================")

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1 Score : {f1:.4f}"
    )

    if len(np.unique(y_test)) == 2:

        roc_auc = roc_auc_score(
            y_test,
            probabilities
        )

        pr_auc = average_precision_score(
            y_test,
            probabilities
        )

        print(
            f"ROC-AUC  : {roc_auc:.4f}"
        )

        print(
            f"PR-AUC   : {pr_auc:.4f}"
        )

    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )

    # ========================================================
    # CLASSIFICATION REPORT
    # ========================================================

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
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
    print("180-DAY CHURN PREDICTION EXPERIMENT")
    print("============================================")

    print(
        f"\nObservation period ends: "
        f"{OBSERVATION_END.date()}"
    )

    print(
        f"Future prediction period: "
        f"{(OBSERVATION_END + pd.Timedelta(days=1)).date()} "
        f"to "
        f"{PREDICTION_END.date()}"
    )

    print(
        f"Churn definition: "
        f"No purchase during next {CHURN_DAYS} days"
    )

    transactions = load_data()

    features = create_features(
        transactions
    )

    labels = create_future_labels(
        transactions,
        features
    )

    train_model(
        features,
        labels
    )


if __name__ == "__main__":
    main()