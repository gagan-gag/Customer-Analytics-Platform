"""
Analytics Service - ML-powered analytics operations
"""
from sqlalchemy.orm import Session
from database import models, schemas
from models.rfm_segmentation import RFMSegmentation
from models.churn_predictor import ChurnPredictor
from models.clv_estimator import CLVEstimator
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List


class AnalyticsService:
    """Service for analytics and ML operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rfm_model = RFMSegmentation()
        self.churn_model = ChurnPredictor()
        self.clv_model = CLVEstimator()
    
    def _get_customers_df(self) -> pd.DataFrame:
        """Get customers as DataFrame"""
        customers = self.db.query(models.Customer).all()
        return pd.DataFrame([{
            'customer_id': c.customer_id,
            'name': c.name,
            'email': c.email,
            'country': c.country,
            'city': c.city,
            'registration_date': c.registration_date,
            'id': c.id
        } for c in customers])
    
    def _get_transactions_df(self) -> pd.DataFrame:
        """Get transactions as DataFrame"""
        transactions = self.db.query(models.Transaction).all()
        return pd.DataFrame([{
            'transaction_id': t.transaction_id,
            'customer_id': (self.db.get(models.Customer, t.customer_id).customer_id
                            if self.db.get(models.Customer, t.customer_id) else None),
            'transaction_date': t.transaction_date,
            'amount': t.amount,
            'quantity': t.quantity,
            'product_category': t.product_category
        } for t in transactions])
    
    def train_rfm_model(self) -> Dict:
        """Train RFM segmentation model"""
        transactions_df = self._get_transactions_df()
        
        if len(transactions_df) == 0:
            return {"error": "No transaction data available"}
        
        rfm_df = self.rfm_model.calculate_rfm(transactions_df)
        
        # Save to database
        for _, row in rfm_df.iterrows():
            customer = self.db.query(models.Customer).filter(
                models.Customer.customer_id == row['customer_id']
            ).first()
            
            if customer:
                # Update or create RFM score
                rfm_score = customer.rfm_score
                if not rfm_score:
                    rfm_score = models.RFMScore(customer_id=customer.id)
                    self.db.add(rfm_score)
                
                rfm_score.recency = int(row['recency'])
                rfm_score.frequency = int(row['frequency'])
                rfm_score.monetary = float(row['monetary'])
                rfm_score.recency_score = int(row['recency_score'])
                rfm_score.frequency_score = int(row['frequency_score'])
                rfm_score.monetary_score = int(row['monetary_score'])
                rfm_score.rfm_score = row['rfm_score']
                rfm_score.segment = row['segment']
                rfm_score.calculated_at = datetime.now()
        
        self.db.commit()
        
        return {
            "customers_segmented": len(rfm_df),
            "segments": rfm_df['segment'].value_counts().to_dict()
        }
    
    def get_rfm_analysis(self, recalculate: bool = False) -> Dict:
        """Get RFM analysis"""
        if recalculate:
            self.train_rfm_model()
        
        rfm_scores = self.db.query(models.RFMScore).all()
        
        return {
            "total_customers": len(rfm_scores),
            "segments": [schemas.RFMScoreResponse.from_orm(r) for r in rfm_scores]
        }
    
    def get_rfm_segment_summary(self) -> List[schemas.RFMSegmentSummary]:
        """Get RFM segment summary"""
        rfm_scores = self.db.query(models.RFMScore).all()
        
        if not rfm_scores:
            return []
        
        df = pd.DataFrame([{
            'segment': r.segment,
            'recency': r.recency,
            'frequency': r.frequency,
            'monetary': r.monetary
        } for r in rfm_scores])
        
        summary = df.groupby('segment').agg({
            'segment': 'count',
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': ['mean', 'sum']
        }).reset_index()
        
        summary.columns = ['segment', 'customer_count', 'avg_recency', 'avg_frequency', 'avg_monetary', 'total_value']
        total = summary['customer_count'].sum()
        summary['percentage'] = (summary['customer_count'] / total * 100).round(2)
        
        return [schemas.RFMSegmentSummary(**row) for row in summary.to_dict('records')]
    
    def train_churn_model(self) -> Dict:
        """Train churn prediction model"""
        customers_df = self._get_customers_df()
        transactions_df = self._get_transactions_df()
        
        if len(transactions_df) == 0:
            return {"error": "No data available"}
        
        # Get RFM scores
        rfm_scores = self.db.query(models.RFMScore).all()
        rfm_df = pd.DataFrame([{
            'customer_id': (self.db.get(models.Customer, r.customer_id).customer_id
                            if self.db.get(models.Customer, r.customer_id) else None),
            'recency': r.recency,
            'frequency': r.frequency,
            'monetary': r.monetary,
            'recency_score': r.recency_score,
            'frequency_score': r.frequency_score,
            'monetary_score': r.monetary_score
        } for r in rfm_scores]) if rfm_scores else None
        
        # Prepare features
        features_df = self.churn_model.prepare_features(customers_df, transactions_df, rfm_df)
        labels_df = self.churn_model.create_churn_labels(transactions_df)
        
        # Train
        metrics = self.churn_model.train(features_df, labels_df)
        self.churn_model.save_model()
        
        # Save metadata
        metadata = models.ModelMetadata(
            model_name="churn",
            model_version="1.0",
            accuracy=metrics.get('accuracy'),
            precision=metrics.get('precision'),
            recall=metrics.get('recall'),
            f1_score=metrics.get('f1_score'),
            training_samples=metrics.get('training_samples'),
            features_used=json.dumps(self.churn_model.feature_columns),
            trained_at=datetime.now(),
            is_active=True
        )
        self.db.add(metadata)
        self.db.commit()
        
        # Predict for all customers
        predictions = self.churn_model.predict(features_df)
        
        # Save predictions
        for _, row in predictions.iterrows():
            customer = self.db.query(models.Customer).filter(
                models.Customer.customer_id == row['customer_id']
            ).first()
            
            if customer:
                churn_pred = customer.churn_prediction
                if not churn_pred:
                    churn_pred = models.ChurnPrediction(customer_id=customer.id)
                    self.db.add(churn_pred)
                
                churn_pred.churn_probability = float(row['churn_probability'])
                churn_pred.churn_risk = row['churn_risk']
                churn_pred.is_churned = bool(row['is_churned'])
                churn_pred.risk_factors = row.get('risk_factors', '')
                churn_pred.predicted_at = datetime.now()
        
        self.db.commit()
        
        return metrics
    
    def get_churn_analysis(self, recalculate: bool = False) -> Dict:
        """Get churn analysis"""
        if recalculate:
            self.train_churn_model()
        
        predictions = self.db.query(models.ChurnPrediction).all()
        
        prediction_list = []
        for p in predictions:
            customer = self.db.get(models.Customer, p.customer_id)
            prediction_list.append(schemas.ChurnPredictionResponse(
                customer_id=p.customer_id,
                customer_str_id=customer.customer_id if customer else str(p.customer_id),
                customer_name=customer.name if customer else "Unknown",
                churn_probability=p.churn_probability or 0.0,
                churn_risk=p.churn_risk or "Low",
                is_churned=p.is_churned or False,
                risk_factors=p.risk_factors,
                predicted_at=p.predicted_at or datetime.now()
            ))
        
        return {
            "total_customers": len(prediction_list),
            "predictions": prediction_list
        }
    
    def get_churn_summary(self) -> schemas.ChurnAnalysisSummary:
        """Get churn summary"""
        predictions = self.db.query(models.ChurnPrediction).all()
        
        if not predictions:
            return schemas.ChurnAnalysisSummary(
                total_customers=0, high_risk_count=0, medium_risk_count=0,
                low_risk_count=0, avg_churn_probability=0
            )
        
        df = pd.DataFrame([{
            'churn_probability': p.churn_probability,
            'churn_risk': p.churn_risk
        } for p in predictions])
        
        return schemas.ChurnAnalysisSummary(
            total_customers=len(df),
            high_risk_count=int((df['churn_risk'] == 'High').sum()),
            medium_risk_count=int((df['churn_risk'] == 'Medium').sum()),
            low_risk_count=int((df['churn_risk'] == 'Low').sum()),
            avg_churn_probability=float(df['churn_probability'].mean())
        )
    
    def train_clv_model(self) -> Dict:
        """Train CLV model"""
        customers_df = self._get_customers_df()
        transactions_df = self._get_transactions_df()
        
        if len(transactions_df) == 0:
            return {"error": "No data available"}
        
        rfm_scores = self.db.query(models.RFMScore).all()
        rfm_df = pd.DataFrame([{
            'customer_id': (self.db.get(models.Customer, r.customer_id).customer_id
                            if self.db.get(models.Customer, r.customer_id) else None),
            'recency': r.recency,
            'frequency': r.frequency,
            'monetary': r.monetary,
            'recency_score': r.recency_score,
            'frequency_score': r.frequency_score,
            'monetary_score': r.monetary_score
        } for r in rfm_scores]) if rfm_scores else None
        
        features_df = self.clv_model.prepare_features(customers_df, transactions_df, rfm_df)
        labels_df = self.clv_model.create_clv_labels(transactions_df)
        
        metrics = self.clv_model.train(features_df, labels_df)
        self.clv_model.save_model()
        
        # Save metadata
        metadata = models.ModelMetadata(
            model_name="clv",
            model_version="1.0",
            rmse=metrics.get('rmse'),
            mae=metrics.get('mae'),
            training_samples=metrics.get('training_samples'),
            features_used=json.dumps(self.clv_model.feature_columns),
            trained_at=datetime.now(),
            is_active=True
        )
        self.db.add(metadata)
        self.db.commit()
        
        # Predict
        predictions = self.clv_model.predict(features_df)
        
        for _, row in predictions.iterrows():
            customer = self.db.query(models.Customer).filter(
                models.Customer.customer_id == row['customer_id']
            ).first()
            
            if customer:
                clv_pred = customer.clv_prediction
                if not clv_pred:
                    clv_pred = models.CLVPrediction(customer_id=customer.id)
                    self.db.add(clv_pred)
                
                clv_pred.predicted_clv = float(row['predicted_clv'])
                clv_pred.clv_segment = row['clv_segment']
                clv_pred.historical_value = float(row['historical_value'])
                clv_pred.avg_order_value = float(row['avg_order_value'])
                clv_pred.purchase_frequency = float(row['purchase_frequency'])
                clv_pred.predicted_at = datetime.now()
        
        self.db.commit()
        
        return metrics
    
    def get_clv_analysis(self, recalculate: bool = False) -> Dict:
        """Get CLV analysis"""
        if recalculate:
            self.train_clv_model()
        
        predictions = self.db.query(models.CLVPrediction).all()
        
        prediction_list = []
        for p in predictions:
            customer = self.db.get(models.Customer, p.customer_id)
            prediction_list.append(schemas.CLVPredictionResponse(
                customer_id=p.customer_id,
                customer_str_id=customer.customer_id if customer else str(p.customer_id),
                customer_name=customer.name if customer else "Unknown",
                predicted_clv=p.predicted_clv or 0.0,
                clv_segment=p.clv_segment or "Unknown",
                historical_value=p.historical_value or 0.0,
                avg_order_value=p.avg_order_value or 0.0,
                purchase_frequency=p.purchase_frequency or 0.0,
                predicted_at=p.predicted_at or datetime.now()
            ))
            
        return {
            "total_customers": len(prediction_list),
            "predictions": prediction_list
        }
    
    def get_clv_summary(self) -> schemas.CLVAnalysisSummary:
        """Get CLV summary"""
        predictions = self.db.query(models.CLVPrediction).all()
        
        if not predictions:
            return schemas.CLVAnalysisSummary(
                total_customers=0, total_predicted_clv=0, avg_clv=0,
                high_value_count=0, medium_value_count=0, low_value_count=0
            )
        
        df = pd.DataFrame([{
            'predicted_clv': p.predicted_clv,
            'clv_segment': p.clv_segment
        } for p in predictions])
        
        return schemas.CLVAnalysisSummary(
            total_customers=len(df),
            total_predicted_clv=float(df['predicted_clv'].sum()),
            avg_clv=float(df['predicted_clv'].mean()),
            high_value_count=int((df['clv_segment'] == 'High Value').sum()),
            medium_value_count=int((df['clv_segment'] == 'Medium Value').sum()),
            low_value_count=int((df['clv_segment'] == 'Low Value').sum())
        )
    
    def get_dashboard_metrics(self) -> schemas.DashboardMetrics:
        """Get comprehensive dashboard metrics"""
        customers = self.db.query(models.Customer).all()
        transactions = self.db.query(models.Transaction).all()
        
        total_revenue = sum(t.amount for t in transactions)
        total_transactions = len(transactions)
        avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Active customers (purchased in last 90 days)
        recent_date = datetime.now() - timedelta(days=90)
        active_customers = len(set([
            t.customer_id for t in transactions 
            if t.transaction_date >= recent_date
        ]))
        
        # Churn rate
        churn_predictions = self.db.query(models.ChurnPrediction).all()
        churn_rate = sum(1 for p in churn_predictions if p.is_churned) / len(churn_predictions) if churn_predictions else 0
        
        # CLV
        clv_predictions = self.db.query(models.CLVPrediction).all()
        avg_clv = sum(p.predicted_clv for p in clv_predictions) / len(clv_predictions) if clv_predictions else 0
        
        # Segment distribution
        rfm_scores = self.db.query(models.RFMScore).all()
        segment_dist = {}
        for r in rfm_scores:
            segment_dist[r.segment] = segment_dist.get(r.segment, 0) + 1
        
        segment_distribution = [{"segment": k, "count": v} for k, v in segment_dist.items()]
        
        return schemas.DashboardMetrics(
            total_customers=len(customers),
            total_revenue=total_revenue,
            avg_order_value=avg_order_value,
            total_transactions=total_transactions,
            active_customers=active_customers,
            churn_rate=churn_rate,
            avg_customer_lifetime_value=avg_clv,
            segment_distribution=segment_distribution,
            revenue_trend=[],
            customer_acquisition_trend=[]
        )
    
    def export_analytics_report(self, report_type: str = "full", format: str = "csv") -> str:
        """Export analytics report"""
        os.makedirs("./exports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if report_type == "rfm":
            rfm_scores = self.db.query(models.RFMScore).all()
            data = [{
                'customer_id': (self.db.get(models.Customer, r.customer_id).customer_id
                                if self.db.get(models.Customer, r.customer_id) else None),
                'segment': r.segment,
                'recency': r.recency,
                'frequency': r.frequency,
                'monetary': r.monetary,
                'rfm_score': r.rfm_score
            } for r in rfm_scores]
            
            df = pd.DataFrame(data)
            filename = f"rfm_analysis_{timestamp}"
        
        elif report_type == "churn":
            predictions = self.db.query(models.ChurnPrediction).all()
            data = [{
                'customer_id': (self.db.get(models.Customer, p.customer_id).customer_id
                                if self.db.get(models.Customer, p.customer_id) else None),
                'churn_probability': p.churn_probability,
                'churn_risk': p.churn_risk,
                'is_churned': p.is_churned
            } for p in predictions]
            
            df = pd.DataFrame(data)
            filename = f"churn_analysis_{timestamp}"
        
        elif report_type == "clv":
            predictions = self.db.query(models.CLVPrediction).all()
            data = [{
                'customer_id': (self.db.get(models.Customer, p.customer_id).customer_id
                                if self.db.get(models.Customer, p.customer_id) else None),
                'predicted_clv': p.predicted_clv,
                'clv_segment': p.clv_segment,
                'historical_value': p.historical_value
            } for p in predictions]
            
            df = pd.DataFrame(data)
            filename = f"clv_analysis_{timestamp}"
        
        else:  # full report
            # Combine all analytics
            customers = self.db.query(models.Customer).all()
            data = []
            
            for customer in customers:
                row = {
                    'customer_id': customer.customer_id,
                    'name': customer.name,
                    'email': customer.email
                }
                
                if customer.rfm_score:
                    row.update({
                        'segment': customer.rfm_score.segment,
                        'rfm_score': customer.rfm_score.rfm_score
                    })
                
                if customer.churn_prediction:
                    row.update({
                        'churn_probability': customer.churn_prediction.churn_probability,
                        'churn_risk': customer.churn_prediction.churn_risk
                    })
                
                if customer.clv_prediction:
                    row.update({
                        'predicted_clv': customer.clv_prediction.predicted_clv,
                        'clv_segment': customer.clv_prediction.clv_segment
                    })
                
                data.append(row)
            
            df = pd.DataFrame(data)
            filename = f"full_analytics_{timestamp}"
        
        if format == "excel":
            file_path = f"./exports/{filename}.xlsx"
            df.to_excel(file_path, index=False)
        else:
            file_path = f"./exports/{filename}.csv"
            df.to_csv(file_path, index=False)
        
        return file_path
