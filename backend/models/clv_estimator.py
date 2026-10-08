"""
Customer Lifetime Value (CLV) Estimation Model
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime
import joblib
import os
from typing import Dict
from config import settings


class CLVEstimator:
    """Estimate Customer Lifetime Value"""
    
    def __init__(self):
        self.model = None
        self.feature_columns = []
        self.model_path = os.path.join(settings.MODEL_PATH, "clv_model.pkl")
        os.makedirs(settings.MODEL_PATH, exist_ok=True)
    
    def prepare_features(self, customers_df: pd.DataFrame, transactions_df: pd.DataFrame,
                        rfm_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Prepare features for CLV estimation
        
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
        
        # Calculate customer metrics
        customer_metrics = transactions_df.groupby('customer_id').agg({
            'transaction_date': ['max', 'min', 'count'],
            'amount': ['sum', 'mean', 'std', 'max', 'min'],
            'quantity': ['sum', 'mean']
        }).reset_index()
        
        customer_metrics.columns = [
            'customer_id', 'last_purchase_date', 'first_purchase_date',
            'total_transactions', 'total_spent', 'avg_order_value',
            'std_order_value', 'max_order_value', 'min_order_value',
            'total_quantity', 'avg_quantity'
        ]
        
        # Time-based features
        customer_metrics['customer_lifetime_days'] = (
            customer_metrics['last_purchase_date'] - customer_metrics['first_purchase_date']
        ).dt.days + 1
        
        customer_metrics['days_since_last_purchase'] = (
            reference_date - customer_metrics['last_purchase_date']
        ).dt.days
        
        customer_metrics['purchase_frequency'] = (
            customer_metrics['total_transactions'] / customer_metrics['customer_lifetime_days']
        ).fillna(0)
        
        # Revenue velocity
        customer_metrics['revenue_per_day'] = (
            customer_metrics['total_spent'] / customer_metrics['customer_lifetime_days']
        ).fillna(0)
        
        # Merge with customer data
        customers_copy = customers_df.copy()
        features = customers_copy.merge(customer_metrics, on='customer_id', how='left')
        
        # Customer age
        features['customer_age_days'] = (reference_date - features['registration_date']).dt.days
        
        # Add RFM scores if available
        if rfm_df is not None:
            rfm_features = rfm_df[['customer_id', 'recency', 'frequency', 'monetary',
                                   'recency_score', 'frequency_score', 'monetary_score']]
            features = features.merge(rfm_features, on='customer_id', how='left')
        
        # Calculate trend features (recent vs. historical)
        recent_transactions = transactions_df[
            transactions_df['transaction_date'] >= (reference_date - pd.Timedelta(days=90))
        ]
        
        recent_metrics = recent_transactions.groupby('customer_id').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()
        
        recent_metrics.columns = ['customer_id', 'recent_spent', 'recent_transactions', 'recent_avg_order']
        features = features.merge(recent_metrics, on='customer_id', how='left')
        
        # Trend indicators
        features['spending_trend'] = (
            features['recent_avg_order'] / features['avg_order_value']
        ).fillna(1)
        
        features['activity_trend'] = (
            features['recent_transactions'] / (features['total_transactions'] + 1)
        ).fillna(0)
        
        # Fill missing values
        numeric_columns = features.select_dtypes(include=[np.number]).columns
        features[numeric_columns] = features[numeric_columns].fillna(0)
        
        return features
    
    def create_clv_labels(self, transactions_df: pd.DataFrame, 
                         prediction_months: int = 12) -> pd.DataFrame:
        """
        Create CLV labels (historical total value as proxy for future value)
        
        Args:
            transactions_df: Transaction data
            prediction_months: Months to predict (used for scaling)
        
        Returns:
            DataFrame with customer_id and CLV
        """
        # Calculate total historical value
        clv = transactions_df.groupby('customer_id')['amount'].sum().reset_index()
        clv.columns = ['customer_id', 'historical_clv']
        
        # For training, we use historical CLV as the target
        # In production, this would be actual future value
        clv['target_clv'] = clv['historical_clv']
        
        return clv
    
    def train(self, features_df: pd.DataFrame, labels_df: pd.DataFrame) -> Dict:
        """
        Train the CLV estimation model
        
        Args:
            features_df: Customer features
            labels_df: CLV labels
        
        Returns:
            Dictionary with training metrics
        """
        # Merge features with labels
        data = features_df.merge(labels_df, on='customer_id', how='inner')
        
        # Select feature columns
        exclude_cols = [
            'customer_id', 'name', 'email', 'phone', 'country', 'city',
            'registration_date', 'last_purchase_date', 'first_purchase_date',
            'historical_clv', 'target_clv', 'created_at', 'updated_at'
        ]
        
        self.feature_columns = [col for col in data.columns if col not in exclude_cols]
        
        X = data[self.feature_columns]
        y = data['target_clv']
        
        # Handle any remaining non-numeric columns
        X = X.select_dtypes(include=[np.number])
        self.feature_columns = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=settings.RANDOM_STATE
        )
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=settings.RANDOM_STATE
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2_score': r2_score(y_test, y_pred),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_count': len(self.feature_columns),
            'mean_actual_clv': float(y_test.mean()),
            'mean_predicted_clv': float(y_pred.mean())
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
        Predict CLV for customers
        
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
        predicted_clv = self.model.predict(X)
        
        # Ensure non-negative predictions
        predicted_clv = np.maximum(predicted_clv, 0)
        
        # Create results DataFrame
        results = pd.DataFrame({
            'customer_id': features_df['customer_id'],
            'predicted_clv': predicted_clv,
            'historical_value': features_df.get('total_spent', 0),
            'avg_order_value': features_df.get('avg_order_value', 0),
            'purchase_frequency': features_df.get('purchase_frequency', 0)
        })
        
        # Assign CLV segments safely without pd.qcut crashing on duplicate edges
        p33 = np.percentile(predicted_clv, 33)
        p66 = np.percentile(predicted_clv, 66)
        
        def assign_segment(value):
            if value >= p66 and value > 0:
                return 'High Value'
            elif value >= p33 and value > 0:
                return 'Medium Value'
            else:
                return 'Low Value'
                
        results['clv_segment'] = results['predicted_clv'].apply(assign_segment)
        
        # Calculate ROI potential
        results['roi_potential'] = (
            results['predicted_clv'] / (results['historical_value'] + 1)
        )
        
        return results
    
    def get_clv_insights(self, predictions_df: pd.DataFrame) -> Dict:
        """
        Generate insights from CLV predictions
        
        Args:
            predictions_df: DataFrame with CLV predictions
        
        Returns:
            Dictionary with insights
        """
        insights = {
            'total_predicted_clv': float(predictions_df['predicted_clv'].sum()),
            'avg_predicted_clv': float(predictions_df['predicted_clv'].mean()),
            'median_predicted_clv': float(predictions_df['predicted_clv'].median()),
            'high_value_customers': int((predictions_df['clv_segment'] == 'High Value').sum()),
            'medium_value_customers': int((predictions_df['clv_segment'] == 'Medium Value').sum()),
            'low_value_customers': int((predictions_df['clv_segment'] == 'Low Value').sum()),
            'top_10_percent_value': float(
                predictions_df.nlargest(int(len(predictions_df) * 0.1), 'predicted_clv')['predicted_clv'].sum()
            ),
            'avg_roi_potential': float(predictions_df['roi_potential'].mean())
        }
        
        return insights
    
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
