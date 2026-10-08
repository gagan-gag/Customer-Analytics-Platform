"""
Churn Prediction Model using Random Forest Classifier
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from datetime import datetime, timedelta
import joblib
import os
from typing import Tuple, Dict
from config import settings


class ChurnPredictor:
    """Predict customer churn probability"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = []
        self.model_path = os.path.join(settings.MODEL_PATH, "churn_model.pkl")
        os.makedirs(settings.MODEL_PATH, exist_ok=True)
    
    def prepare_features(self, customers_df: pd.DataFrame, transactions_df: pd.DataFrame, 
                        rfm_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Prepare features for churn prediction
        
        Args:
            customers_df: Customer data
            transactions_df: Transaction data
            rfm_df: Optional RFM scores
        
        Returns:
            DataFrame with features for each customer
        """
        # Ensure datetime columns
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        customers_df['registration_date'] = pd.to_datetime(customers_df['registration_date'])
        
        reference_date = datetime.now()
        
        # Calculate transaction-based features
        customer_features = transactions_df.groupby('customer_id').agg({
            'transaction_date': ['max', 'min', 'count'],
            'amount': ['sum', 'mean', 'std'],
            'quantity': 'sum'
        }).reset_index()
        
        customer_features.columns = [
            'customer_id', 'last_purchase_date', 'first_purchase_date',
            'total_transactions', 'total_spent', 'avg_order_value',
            'std_order_value', 'total_quantity'
        ]
        
        # Calculate time-based features
        customer_features['days_since_last_purchase'] = (
            reference_date - customer_features['last_purchase_date']
        ).dt.days
        
        customer_features['customer_lifetime_days'] = (
            customer_features['last_purchase_date'] - customer_features['first_purchase_date']
        ).dt.days + 1
        
        customer_features['purchase_frequency'] = (
            customer_features['total_transactions'] / customer_features['customer_lifetime_days']
        ).fillna(0)
        
        # Merge with customer data
        customers_df_copy = customers_df.copy()
        features = customers_df_copy.merge(customer_features, on='customer_id', how='left')
        
        # Customer age
        features['customer_age_days'] = (reference_date - features['registration_date']).dt.days
        
        # Add RFM scores if available
        if rfm_df is not None:
            rfm_features = rfm_df[['customer_id', 'recency', 'frequency', 'monetary',
                                   'recency_score', 'frequency_score', 'monetary_score']]
            features = features.merge(rfm_features, on='customer_id', how='left')
        
        # Fill missing values
        numeric_columns = features.select_dtypes(include=[np.number]).columns
        features[numeric_columns] = features[numeric_columns].fillna(0)
        
        return features
    
    def create_churn_labels(self, transactions_df: pd.DataFrame, 
                           churn_threshold_days: int = 180) -> pd.DataFrame:
        """
        Create churn labels based on recency
        
        Args:
            transactions_df: Transaction data
            churn_threshold_days: Days without purchase to consider churned
        
        Returns:
            DataFrame with customer_id and churn label
        """
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        reference_date = datetime.now()
        
        last_purchase = transactions_df.groupby('customer_id')['transaction_date'].max().reset_index()
        last_purchase.columns = ['customer_id', 'last_purchase_date']
        
        last_purchase['days_since_last_purchase'] = (
            reference_date - last_purchase['last_purchase_date']
        ).dt.days
        
        last_purchase['is_churned'] = (
            last_purchase['days_since_last_purchase'] > churn_threshold_days
        ).astype(int)
        
        return last_purchase[['customer_id', 'is_churned']]
    
    def train(self, features_df: pd.DataFrame, labels_df: pd.DataFrame) -> Dict:
        """
        Train the churn prediction model
        
        Args:
            features_df: Customer features
            labels_df: Churn labels
        
        Returns:
            Dictionary with training metrics
        """
        # Merge features with labels
        data = features_df.merge(labels_df, on='customer_id', how='inner')
        
        # Select feature columns
        exclude_cols = [
            'customer_id', 'name', 'email', 'phone', 'country', 'city',
            'registration_date', 'last_purchase_date', 'first_purchase_date',
            'is_churned', 'created_at', 'updated_at'
        ]
        
        self.feature_columns = [col for col in data.columns if col not in exclude_cols]
        
        X = data[self.feature_columns]
        y = data['is_churned']
        
        # Handle any remaining non-numeric columns
        X = X.select_dtypes(include=[np.number])
        self.feature_columns = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=settings.RANDOM_STATE, stratify=y
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=settings.RANDOM_STATE,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_count': len(self.feature_columns)
        }
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        metrics['top_features'] = feature_importance.head(10).to_dict('records')
        
        return metrics
    
    def predict(self, features_df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict churn probability for customers
        
        Args:
            features_df: Customer features
        
        Returns:
            DataFrame with predictions
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first or load a saved model.")
        
        # Prepare features
        X = features_df[self.feature_columns].select_dtypes(include=[np.number])
        
        # Predict
        churn_probability = self.model.predict_proba(X)[:, 1]
        
        # Create results DataFrame
        results = pd.DataFrame({
            'customer_id': features_df['customer_id'],
            'churn_probability': churn_probability
        })
        
        # Assign risk levels
        results['churn_risk'] = pd.cut(
            results['churn_probability'],
            bins=[0, 0.3, 0.6, 1.0],
            labels=['Low', 'Medium', 'High']
        )
        
        results['is_churned'] = (results['churn_probability'] >= settings.CHURN_THRESHOLD).astype(int)
        
        # Get top risk factors
        results['risk_factors'] = results.apply(
            lambda row: self._get_risk_factors(
                features_df[features_df['customer_id'] == row['customer_id']].iloc[0]
            ),
            axis=1
        )
        
        return results
    
    def _get_risk_factors(self, customer_features: pd.Series) -> str:
        """Identify key risk factors for a customer"""
        factors = []
        
        if customer_features.get('days_since_last_purchase', 0) > 90:
            factors.append("Long time since last purchase")
        
        if customer_features.get('purchase_frequency', 0) < 0.01:
            factors.append("Low purchase frequency")
        
        if customer_features.get('total_transactions', 0) <= 2:
            factors.append("Very few transactions")
        
        if customer_features.get('avg_order_value', 0) < 50:
            factors.append("Low average order value")
        
        if customer_features.get('recency_score', 5) <= 2:
            factors.append("Poor recency score")
        
        return ", ".join(factors) if factors else "No major risk factors"
    
    def save_model(self):
        """Save trained model to disk"""
        if self.model is None:
            raise ValueError("No model to save")
        
        model_data = {
            'model': self.model,
            'feature_columns': self.feature_columns
        }
        joblib.dump(model_data, self.model_path)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        model_data = joblib.load(self.model_path)
        self.model = model_data['model']
        self.feature_columns = model_data['feature_columns']
        print(f"Model loaded from {self.model_path}")
