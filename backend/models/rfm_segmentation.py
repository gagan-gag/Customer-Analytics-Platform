"""
RFM (Recency, Frequency, Monetary) Segmentation Model
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from config import settings


class RFMSegmentation:
    """RFM Analysis and Customer Segmentation"""
    
    def __init__(self):
        self.rfm_labels = settings.RFM_LABELS
    
    def calculate_rfm(self, transactions_df: pd.DataFrame, reference_date: datetime = None) -> pd.DataFrame:
        """
        Calculate RFM metrics for each customer
        
        Args:
            transactions_df: DataFrame with columns [customer_id, transaction_date, amount]
            reference_date: Reference date for recency calculation (default: today)
        
        Returns:
            DataFrame with RFM metrics and scores
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        # Ensure transaction_date is datetime
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        
        # Calculate RFM metrics
        rfm = transactions_df.groupby('customer_id').agg({
            'transaction_date': lambda x: (reference_date - x.max()).days,  # Recency
            'transaction_id': 'count',  # Frequency
            'amount': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
        
        # Calculate RFM scores (1-5, where 5 is best)
        rfm['recency_score'] = pd.qcut(
            rfm['recency'], 
            q=5, 
            labels=[5, 4, 3, 2, 1],  # Lower recency is better
            duplicates='drop'
        )
        
        rfm['frequency_score'] = pd.qcut(
            rfm['frequency'], 
            q=5, 
            labels=[1, 2, 3, 4, 5],  # Higher frequency is better
            duplicates='drop'
        )
        
        rfm['monetary_score'] = pd.qcut(
            rfm['monetary'], 
            q=5, 
            labels=[1, 2, 3, 4, 5],  # Higher monetary is better
            duplicates='drop'
        )
        
        # Convert scores to integers
        rfm['recency_score'] = rfm['recency_score'].astype(int)
        rfm['frequency_score'] = rfm['frequency_score'].astype(int)
        rfm['monetary_score'] = rfm['monetary_score'].astype(int)
        
        # Create combined RFM score
        rfm['rfm_score'] = (
            rfm['recency_score'].astype(str) + 
            rfm['frequency_score'].astype(str) + 
            rfm['monetary_score'].astype(str)
        )
        
        # Assign segments
        rfm['segment'] = rfm.apply(self._assign_segment, axis=1)
        
        return rfm
    
    def _assign_segment(self, row) -> str:
        """Assign customer segment based on RFM scores"""
        r, f, m = row['recency_score'], row['frequency_score'], row['monetary_score']
        
        # Champions: High value, frequent, recent customers
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        
        # Loyal Customers: Regular customers with good value
        elif r >= 3 and f >= 3 and m >= 3:
            return "Loyal Customers"
        
        # Potential Loyalists: Recent customers with potential
        elif r >= 3 and f <= 3 and m <= 3:
            return "Potential Loyalists"
        
        # New Customers: Recent first-time buyers
        elif r >= 4 and f == 1:
            return "New Customers"
        
        # Promising: Recent customers with low frequency
        elif r >= 3 and f == 1:
            return "Promising"
        
        # Need Attention: Above average but declining
        elif r >= 3 and f >= 3:
            return "Need Attention"
        
        # About to Sleep: Below average, need reactivation
        elif r >= 2 and r <= 3:
            return "About to Sleep"
        
        # At Risk: High value customers who haven't purchased recently
        elif r <= 2 and f >= 3 and m >= 3:
            return "At Risk"
        
        # Cannot Lose Them: Very high value but haven't purchased recently
        elif r <= 2 and f >= 4 and m >= 4:
            return "Cannot Lose Them"
        
        # Hibernating: Low engagement across all metrics
        elif r <= 2 and f <= 2 and m <= 2:
            return "Hibernating"
        
        # Lost: Lowest engagement
        elif r == 1 and f <= 2:
            return "Lost"
        
        else:
            return "Other"
    
    def get_segment_summary(self, rfm_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get summary statistics for each segment
        
        Args:
            rfm_df: DataFrame with RFM scores and segments
        
        Returns:
            DataFrame with segment summaries
        """
        summary = rfm_df.groupby('segment').agg({
            'customer_id': 'count',
            'recency': 'mean',
            'frequency': 'mean',
            'monetary': ['mean', 'sum']
        }).reset_index()
        
        summary.columns = [
            'segment', 'customer_count', 'avg_recency', 
            'avg_frequency', 'avg_monetary', 'total_value'
        ]
        
        # Calculate percentage
        total_customers = summary['customer_count'].sum()
        summary['percentage'] = (summary['customer_count'] / total_customers * 100).round(2)
        
        # Round numeric columns
        summary['avg_recency'] = summary['avg_recency'].round(1)
        summary['avg_frequency'] = summary['avg_frequency'].round(1)
        summary['avg_monetary'] = summary['avg_monetary'].round(2)
        summary['total_value'] = summary['total_value'].round(2)
        
        # Sort by total value descending
        summary = summary.sort_values('total_value', ascending=False)
        
        return summary
    
    def get_segment_recommendations(self, segment: str) -> Dict:
        """
        Get marketing recommendations for a segment
        
        Args:
            segment: Customer segment name
        
        Returns:
            Dictionary with recommendations
        """
        recommendations = {
            "Champions": {
                "strategy": "Reward and retain",
                "priority": "High",
                "actions": [
                    "Offer exclusive VIP benefits",
                    "Early access to new products",
                    "Personalized recommendations",
                    "Loyalty rewards program",
                    "Request referrals and reviews"
                ],
                "expected_impact": "Maintain high value and advocacy"
            },
            "Loyal Customers": {
                "strategy": "Upsell and cross-sell",
                "priority": "High",
                "actions": [
                    "Recommend complementary products",
                    "Offer bundle deals",
                    "Provide loyalty points",
                    "Send personalized offers",
                    "Encourage subscription services"
                ],
                "expected_impact": "Increase purchase frequency and value"
            },
            "Potential Loyalists": {
                "strategy": "Nurture and engage",
                "priority": "Medium",
                "actions": [
                    "Send targeted email campaigns",
                    "Offer time-limited discounts",
                    "Provide product education",
                    "Encourage repeat purchases",
                    "Build brand connection"
                ],
                "expected_impact": "Convert to loyal customers"
            },
            "New Customers": {
                "strategy": "Onboard and activate",
                "priority": "Medium",
                "actions": [
                    "Welcome email series",
                    "First purchase discount for next order",
                    "Product tutorials and guides",
                    "Encourage profile completion",
                    "Gather feedback"
                ],
                "expected_impact": "Drive second purchase"
            },
            "Promising": {
                "strategy": "Activate quickly",
                "priority": "Medium",
                "actions": [
                    "Limited-time offers",
                    "Free shipping incentives",
                    "Product recommendations",
                    "Engagement campaigns",
                    "Build purchase habit"
                ],
                "expected_impact": "Increase frequency before they cool off"
            },
            "Need Attention": {
                "strategy": "Re-engage",
                "priority": "Medium",
                "actions": [
                    "Win-back campaigns",
                    "Special reactivation offers",
                    "Survey for feedback",
                    "Highlight new products",
                    "Personalized communication"
                ],
                "expected_impact": "Prevent churn"
            },
            "About to Sleep": {
                "strategy": "Reactivate urgently",
                "priority": "High",
                "actions": [
                    "Aggressive win-back offers",
                    "Remind of account value",
                    "Survey to understand issues",
                    "Exclusive comeback deals",
                    "Multi-channel outreach"
                ],
                "expected_impact": "Prevent transition to lost"
            },
            "At Risk": {
                "strategy": "Win back high-value customers",
                "priority": "Critical",
                "actions": [
                    "Personalized win-back campaigns",
                    "VIP customer service outreach",
                    "Significant discount offers",
                    "Understand pain points",
                    "Exclusive incentives"
                ],
                "expected_impact": "Recover high-value relationships"
            },
            "Cannot Lose Them": {
                "strategy": "Recover immediately",
                "priority": "Critical",
                "actions": [
                    "Direct personal outreach",
                    "Executive-level engagement",
                    "Major incentives and offers",
                    "Address specific concerns",
                    "VIP treatment and perks"
                ],
                "expected_impact": "Prevent loss of top customers"
            },
            "Hibernating": {
                "strategy": "Low-cost reactivation",
                "priority": "Low",
                "actions": [
                    "Automated email campaigns",
                    "Deep discount offers",
                    "Highlight major changes",
                    "Last-chance messaging",
                    "Minimal investment approach"
                ],
                "expected_impact": "Cost-effective recovery attempts"
            },
            "Lost": {
                "strategy": "Minimal effort or remove",
                "priority": "Low",
                "actions": [
                    "Final win-back attempt",
                    "Survey for insights",
                    "Opt-out option",
                    "Learn from feedback",
                    "Consider list removal"
                ],
                "expected_impact": "Gather insights, clean database"
            }
        }
        
        return recommendations.get(segment, {
            "strategy": "Analyze further",
            "priority": "Medium",
            "actions": ["Conduct detailed analysis"],
            "expected_impact": "Better understanding"
        })
