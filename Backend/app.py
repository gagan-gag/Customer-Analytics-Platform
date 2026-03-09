"""
FastAPI Application - Customer Segmentation & Retention Analytics Platform
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import pandas as pd
import io
import os
from config import settings
from database.database import get_db, init_db
from database import models, schemas
from services.customer_service import CustomerService
from services.analytics_service import AnalyticsService
from services.recommendation_service import RecommendationService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables and handle startup/shutdown"""
    init_db()
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} started successfully!")
    yield

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-ready Customer Analytics Platform with ML-powered insights",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lifespan events are handled in the lifespan function defined above


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@app.get(f"{settings.API_PREFIX}/customers", response_model=List[schemas.CustomerResponse])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get list of customers"""
    service = CustomerService(db)
    return service.get_customers(skip=skip, limit=limit)


@app.get(f"{settings.API_PREFIX}/customers/{{customer_id}}", response_model=schemas.CustomerDetailedAnalytics)
async def get_customer_details(customer_id: str, db: Session = Depends(get_db)):
    """Get detailed analytics for a specific customer"""
    service = CustomerService(db)
    customer = service.get_customer_by_customer_id(customer_id)
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return service.get_customer_analytics(customer_id)


@app.post(f"{settings.API_PREFIX}/customers/upload", response_model=schemas.UploadResponse)
async def upload_customer_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload customer and transaction data from CSV/Excel file"""
    service = CustomerService(db)
    
    # Read file
    contents = await file.read()
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")
        
        result = service.import_data(df)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get(f"{settings.API_PREFIX}/analytics/dashboard", response_model=schemas.DashboardMetrics)
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get comprehensive dashboard metrics"""
    service = AnalyticsService(db)
    return service.get_dashboard_metrics()


@app.get(f"{settings.API_PREFIX}/analytics/rfm")
async def get_rfm_analysis(
    recalculate: bool = False,
    db: Session = Depends(get_db)
):
    """Get RFM segmentation analysis"""
    service = AnalyticsService(db)
    return service.get_rfm_analysis(recalculate=recalculate)


@app.get(f"{settings.API_PREFIX}/analytics/rfm/segments")
async def get_rfm_segments(db: Session = Depends(get_db)):
    """Get RFM segment summary"""
    service = AnalyticsService(db)
    return service.get_rfm_segment_summary()


@app.get(f"{settings.API_PREFIX}/analytics/churn")
async def get_churn_analysis(
    recalculate: bool = False,
    db: Session = Depends(get_db)
):
    """Get churn prediction analysis"""
    service = AnalyticsService(db)
    return service.get_churn_analysis(recalculate=recalculate)


@app.get(f"{settings.API_PREFIX}/analytics/churn/summary")
async def get_churn_summary(db: Session = Depends(get_db)):
    """Get churn analysis summary"""
    service = AnalyticsService(db)
    return service.get_churn_summary()


@app.get(f"{settings.API_PREFIX}/analytics/clv")
async def get_clv_analysis(
    recalculate: bool = False,
    db: Session = Depends(get_db)
):
    """Get CLV prediction analysis"""
    service = AnalyticsService(db)
    return service.get_clv_analysis(recalculate=recalculate)


@app.get(f"{settings.API_PREFIX}/analytics/clv/summary")
async def get_clv_summary(db: Session = Depends(get_db)):
    """Get CLV analysis summary"""
    service = AnalyticsService(db)
    return service.get_clv_summary()


# ============================================================================
# ML MODEL ENDPOINTS
# ============================================================================

@app.post(f"{settings.API_PREFIX}/models/train")
async def train_models(
    model_type: Optional[str] = Query(None, description="Model type: rfm, churn, clv, or all"),
    db: Session = Depends(get_db)
):
    """Train or retrain ML models"""
    service = AnalyticsService(db)
    
    if model_type == "all" or model_type is None:
        results = {
            "rfm": service.train_rfm_model(),
            "churn": service.train_churn_model(),
            "clv": service.train_clv_model()
        }
        return {"message": "All models trained successfully", "results": results}
    
    elif model_type == "rfm":
        result = service.train_rfm_model()
        return {"message": "RFM model trained successfully", "result": result}
    
    elif model_type == "churn":
        result = service.train_churn_model()
        return {"message": "Churn model trained successfully", "result": result}
    
    elif model_type == "clv":
        result = service.train_clv_model()
        return {"message": "CLV model trained successfully", "result": result}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid model type")


@app.get(f"{settings.API_PREFIX}/models/performance")
async def get_model_performance(db: Session = Depends(get_db)):
    """Get ML model performance metrics"""
    metadata = db.query(models.ModelMetadata).filter(
        models.ModelMetadata.is_active == True
    ).all()
    
    return [schemas.ModelPerformanceResponse.from_orm(m) for m in metadata]


# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================

@app.get(f"{settings.API_PREFIX}/recommendations")
async def get_recommendations(
    segment: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get retention strategy recommendations"""
    service = RecommendationService(db)
    return service.get_customer_recommendations(segment=segment, limit=limit)


@app.get(f"{settings.API_PREFIX}/recommendations/strategies")
async def get_retention_strategies(db: Session = Depends(get_db)):
    """Get retention strategies for all segments"""
    service = RecommendationService(db)
    return service.get_all_retention_strategies()


@app.get(f"{settings.API_PREFIX}/recommendations/customer/{{customer_id}}")
async def get_customer_recommendation(customer_id: str, db: Session = Depends(get_db)):
    """Get personalized recommendations for a specific customer"""
    service = RecommendationService(db)
    recommendation = service.get_customer_specific_recommendation(customer_id)
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return recommendation


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@app.get(f"{settings.API_PREFIX}/export/customers")
async def export_customers(
    format: str = Query("csv", description="Export format: csv or excel"),
    db: Session = Depends(get_db)
):
    """Export customer data"""
    service = CustomerService(db)
    file_path = service.export_customers(format=format)
    
    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=os.path.basename(file_path)
    )


@app.get(f"{settings.API_PREFIX}/export/analytics")
async def export_analytics(
    report_type: str = Query("full", description="Report type: full, rfm, churn, or clv"),
    format: str = Query("csv", description="Export format: csv or excel"),
    db: Session = Depends(get_db)
):
    """Export analytics reports"""
    service = AnalyticsService(db)
    file_path = service.export_analytics_report(report_type=report_type, format=format)
    
    return FileResponse(
        file_path,
        media_type='application/octet-stream',
        filename=os.path.basename(file_path)
    )


# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.get(f"{settings.API_PREFIX}/stats/overview")
async def get_statistics_overview(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_customers = db.query(models.Customer).count()
    total_transactions = db.query(models.Transaction).count()
    total_revenue = db.query(models.Transaction).with_entities(
        models.Transaction.amount
    ).all()
    total_revenue = sum([t[0] for t in total_revenue]) if total_revenue else 0
    
    return {
        "total_customers": total_customers,
        "total_transactions": total_transactions,
        "total_revenue": round(total_revenue, 2),
        "avg_revenue_per_customer": round(total_revenue / total_customers, 2) if total_customers > 0 else 0
    }



# ============================================================================
# DATA MANAGEMENT ENDPOINTS
# ============================================================================

@app.delete(f"{settings.API_PREFIX}/data/reset")
async def reset_all_data(db: Session = Depends(get_db)):
    """
    Delete ALL data from the database — customers, transactions, 
    RFM scores, churn predictions, CLV predictions, and model metadata.
    Use this to clear previously uploaded data before loading a new dataset.
    """
    try:
        # Delete in order to avoid FK constraint violations
        clv_count  = db.query(models.CLVPrediction).count()
        churn_count = db.query(models.ChurnPrediction).count()
        rfm_count   = db.query(models.RFMScore).count()
        txn_count   = db.query(models.Transaction).count()
        cust_count  = db.query(models.Customer).count()
        meta_count  = db.query(models.ModelMetadata).count()

        db.query(models.CLVPrediction).delete()
        db.query(models.ChurnPrediction).delete()
        db.query(models.RFMScore).delete()
        db.query(models.ModelMetadata).delete()
        db.query(models.Transaction).delete()
        db.query(models.Customer).delete()
        db.commit()

        return {
            "success": True,
            "message": "All data cleared successfully. You can now upload a new dataset.",
            "deleted": {
                "customers": cust_count,
                "transactions": txn_count,
                "rfm_scores": rfm_count,
                "churn_predictions": churn_count,
                "clv_predictions": clv_count,
                "model_metadata": meta_count
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reset data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
