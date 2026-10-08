"""
Recommendation Service - Generate retention strategies
"""
from sqlalchemy.orm import Session
from database import models, schemas
from models.rfm_segmentation import RFMSegmentation
from typing import List, Optional, Dict


class RecommendationService:
    """Service for generating customer retention recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rfm_model = RFMSegmentation()
    
    def get_all_retention_strategies(self) -> List[schemas.RetentionStrategy]:
        """Get retention strategies for all segments"""
        segments = [
            "Champions", "Loyal Customers", "Potential Loyalists", "New Customers",
            "Promising", "Need Attention", "About to Sleep", "At Risk",
            "Cannot Lose Them", "Hibernating", "Lost"
        ]
        
        strategies = []
        for segment in segments:
            strategy = self.rfm_model.get_segment_recommendations(segment)
            strategies.append(schemas.RetentionStrategy(
                segment=segment,
                strategy=strategy['strategy'],
                priority=strategy['priority'],
                actions=strategy['actions'],
                expected_impact=strategy['expected_impact']
            ))
        
        return strategies
    
    def get_customer_recommendations(self, segment: Optional[str] = None, 
                                    limit: int = 50) -> List[schemas.RecommendationResponse]:
        """Get customer-specific recommendations"""
        # Use outerjoin so customers without RFM scores are still included
        query = self.db.query(models.Customer).outerjoin(models.RFMScore)
        
        if segment:
            query = query.filter(models.RFMScore.segment == segment)
        
        customers = query.limit(limit).all()
        
        recommendations = []
        for customer in customers:
            # Use the customer's RFM segment if available, else fall back to a default
            cust_segment = customer.rfm_score.segment if customer.rfm_score else "Need Attention"
            strategy = self.rfm_model.get_segment_recommendations(cust_segment)
            
            churn_risk = "Unknown"
            if customer.churn_prediction:
                churn_risk = customer.churn_prediction.churn_risk
            
            clv_segment = "Unknown"
            if customer.clv_prediction:
                clv_segment = customer.clv_prediction.clv_segment
            
            recommendations.append(schemas.RecommendationResponse(
                customer_id=customer.id,
                customer_name=customer.name,
                segment=cust_segment,
                churn_risk=churn_risk,
                clv_segment=clv_segment,
                recommended_actions=strategy['actions'],
                priority=strategy['priority']
            ))
        
        return recommendations
    
    def get_customer_specific_recommendation(self, customer_id: str) -> Optional[schemas.RecommendationResponse]:
        """Get recommendation for a specific customer"""
        customer = self.db.query(models.Customer).filter(
            models.Customer.customer_id == customer_id
        ).first()
        
        if not customer or not customer.rfm_score:
            return None
        
        segment = customer.rfm_score.segment
        strategy = self.rfm_model.get_segment_recommendations(segment)
        
        churn_risk = "Unknown"
        if customer.churn_prediction:
            churn_risk = customer.churn_prediction.churn_risk
        
        clv_segment = "Unknown"
        if customer.clv_prediction:
            clv_segment = customer.clv_prediction.clv_segment
        
        return schemas.RecommendationResponse(
            customer_id=customer.id,
            customer_name=customer.name,
            segment=segment,
            churn_risk=churn_risk,
            clv_segment=clv_segment,
            recommended_actions=strategy['actions'],
            priority=strategy['priority']
        )
