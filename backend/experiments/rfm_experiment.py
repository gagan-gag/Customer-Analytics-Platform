import pandas as pd
import numpy as np


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = "data/transactions.csv"

REFERENCE_DATE = pd.Timestamp("2025-08-22")


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("Loading transaction data...")

    df = pd.read_csv(DATA_PATH)

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"]
    )

    # Use only historical transactions.
    df = df[
        df["transaction_date"] <= REFERENCE_DATE
    ].copy()

    print(f"Transactions used: {len(df)}")
    print(f"Customers: {df['customer_id'].nunique()}")

    print(
        f"Date range: "
        f"{df['transaction_date'].min().date()} "
        f"to "
        f"{df['transaction_date'].max().date()}"
    )

    return df


# ============================================================
# CALCULATE RFM
# ============================================================

def calculate_rfm(df):

    print("\nCalculating RFM values...")

    rfm = df.groupby("customer_id").agg(

        last_purchase=("transaction_date", "max"),

        frequency=("transaction_id", "count"),

        monetary=("amount", "sum")

    ).reset_index()

    # Recency = number of days since last purchase.
    rfm["recency"] = (
        REFERENCE_DATE - rfm["last_purchase"]
    ).dt.days

    return rfm


# ============================================================
# CREATE RFM SCORES
# ============================================================

def create_rfm_scores(rfm):

    print("Creating RFM scores...")

    # Rank first so duplicate values do not break qcut.
    rfm["recency_rank"] = (
        rfm["recency"]
        .rank(method="first")
    )

    rfm["frequency_rank"] = (
        rfm["frequency"]
        .rank(method="first")
    )

    rfm["monetary_rank"] = (
        rfm["monetary"]
        .rank(method="first")
    )

    # Recency:
    # Lower number of days = better customer.
    rfm["recency_score"] = pd.qcut(
        rfm["recency_rank"],
        q=5,
        labels=[5, 4, 3, 2, 1]
    ).astype(int)

    # Frequency:
    # Higher number of purchases = better.
    rfm["frequency_score"] = pd.qcut(
        rfm["frequency_rank"],
        q=5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Monetary:
    # Higher spending = better.
    rfm["monetary_score"] = pd.qcut(
        rfm["monetary_rank"],
        q=5,
        labels=[1, 2, 3, 4, 5]
    ).astype(int)

    rfm["rfm_score"] = (
        rfm["recency_score"].astype(str)
        + rfm["frequency_score"].astype(str)
        + rfm["monetary_score"].astype(str)
    )

    return rfm


# ============================================================
# ASSIGN CUSTOMER SEGMENTS
# ============================================================

def assign_segments(rfm):

    def get_segment(row):

        r = row["recency_score"]
        f = row["frequency_score"]
        m = row["monetary_score"]

        # Champions
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"

        # Loyal Customers
        elif r >= 3 and f >= 4 and m >= 3:
            return "Loyal Customers"

        # Potential Loyalists
        elif r >= 4 and f >= 2 and m >= 2:
            return "Potential Loyalists"

        # New Customers
        elif r >= 4 and f <= 2:
            return "New Customers"

        # Promising
        elif r >= 3 and f <= 2 and m >= 2:
            return "Promising"

        # Need Attention
        elif r == 3 and f >= 3:
            return "Need Attention"

        # About to Sleep
        elif r == 2 and f <= 3:
            return "About to Sleep"

        # At Risk
        elif r <= 2 and f >= 3:
            return "At Risk"

        # Cannot Lose Them
        elif r <= 2 and f >= 4 and m >= 4:
            return "Cannot Lose Them"

        # Hibernating
        elif r == 1 and f <= 2:
            return "Hibernating"

        # Lost
        elif r == 1 and f == 3:
            return "Lost"

        else:
            return "Other"

    rfm["segment"] = rfm.apply(
        get_segment,
        axis=1
    )

    return rfm


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(rfm):

    print("\n========================================")
    print("RFM SEGMENTATION RESULTS")
    print("========================================")

    print(
        f"Total customers segmented: "
        f"{len(rfm)}"
    )

    # --------------------------------------------------------
    # SEGMENT SUMMARY
    # --------------------------------------------------------

    summary = (
        rfm.groupby("segment")
        .agg(
            customers=("customer_id", "count"),

            avg_recency=("recency", "mean"),

            avg_frequency=("frequency", "mean"),

            avg_monetary=("monetary", "mean")
        )
        .sort_values(
            "customers",
            ascending=False
        )
    )

    summary["percentage"] = (
        summary["customers"]
        / len(rfm)
        * 100
    )

    summary = summary[
        [
            "customers",
            "percentage",
            "avg_recency",
            "avg_frequency",
            "avg_monetary"
        ]
    ]

    print("\nSegment Summary:")

    print(
        summary.round(2).to_string()
    )

    # --------------------------------------------------------
    # SCORE SUMMARY
    # --------------------------------------------------------

    print("\nRFM Score Distribution:")

    score_distribution = (
        rfm["rfm_score"]
        .value_counts()
        .sort_index()
    )

    print(
        score_distribution.to_string()
    )

    # --------------------------------------------------------
    # TOP CUSTOMERS
    # --------------------------------------------------------

    print("\nTop 10 Customers by Monetary Value:")

    top_customers = rfm.sort_values(
        "monetary",
        ascending=False
    ).head(10)

    print(
        top_customers[
            [
                "customer_id",
                "recency",
                "frequency",
                "monetary",
                "rfm_score",
                "segment"
            ]
        ].round(2).to_string(
            index=False
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("============================================")
    print("RFM CUSTOMER SEGMENTATION EXPERIMENT")
    print("============================================")

    print(
        f"\nReference date: "
        f"{REFERENCE_DATE.date()}"
    )

    print(
        "\nRFM dimensions:"
    )

    print(
        "Recency   = Days since last purchase"
    )

    print(
        "Frequency = Number of purchases"
    )

    print(
        "Monetary  = Total customer spending"
    )

    df = load_data()

    rfm = calculate_rfm(
        df
    )

    rfm = create_rfm_scores(
        rfm
    )

    rfm = assign_segments(
        rfm
    )

    display_results(
        rfm
    )


if __name__ == "__main__":
    main()