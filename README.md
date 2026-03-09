# Customer Segmentation & Retention Analytics Platform

A production-ready, end-to-end analytics web application for customer behavior analysis, segmentation, churn prediction, and retention strategies.

## 🚀 Features

### Core Analytics

- **RFM Segmentation**: Recency, Frequency, Monetary analysis
- **Churn Prediction**: ML-based customer churn forecasting
- **Customer Lifetime Value (CLV)**: Predictive CLV estimation
- **Retention Strategies**: AI-driven actionable recommendations

### Data Management

- ✅ Synthetic data generation for demos
- ✅ CSV/Excel file upload
- ✅ Database integration
- ✅ Export reports (PDF, CSV, Excel)

### Dashboard Features

- Real-time analytics visualization
- Customer segment comparison views
- Interactive charts and metrics
- Drill-down capabilities
- Export and sharing functionality

## 🛠️ Tech Stack

### Backend

- **Framework**: FastAPI (Python 3.9+)
- **ML/Analytics**: scikit-learn, pandas, numpy
- **Database**: SQLAlchemy + SQLite
- **API**: RESTful with automatic OpenAPI docs

### Frontend

- **Framework**: React 18+ with Vite
- **UI Library**: Material-UI / Ant Design
- **Charts**: Recharts
- **State Management**: React Query + Context API
- **Styling**: CSS Modules + Tailwind CSS

### ML Models

- **Segmentation**: K-Means clustering with RFM features
- **Churn Prediction**: Random Forest Classifier
- **CLV Estimation**: Gradient Boosting Regressor
- **Feature Engineering**: Custom transformers

## 📦 Installation

### Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## 🎯 Quick Start

1. **Generate Demo Data**

   ```bash
   cd backend
   python utils/generate_data.py
   ```

2. **Start Backend Server**

   ```bash
   cd backend
   uvicorn app:app --reload
   ```

3. **Start Frontend**

   ```bash
   cd frontend
   npm run dev
   ```

4. **Access Application**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/docs

## 📊 API Endpoints

### Customer Management

- `GET /api/customers` - List all customers
- `POST /api/customers/upload` - Upload customer data (CSV/Excel)
- `GET /api/customers/{id}` - Get customer details

### Analytics

- `GET /api/analytics/rfm` - RFM segmentation analysis
- `GET /api/analytics/churn` - Churn prediction results
- `GET /api/analytics/clv` - Customer lifetime value estimates
- `GET /api/analytics/dashboard` - Dashboard summary metrics

### ML Models

- `POST /api/models/train` - Train/retrain ML models
- `GET /api/models/performance` - Model performance metrics
- `POST /api/predictions/churn` - Predict churn for customer(s)
- `POST /api/predictions/clv` - Predict CLV for customer(s)

### Reports

- `GET /api/reports/export` - Export analytics reports
- `GET /api/recommendations` - Get retention strategies

## 🏗️ Project Structure

```
customer-analytics/
├── backend/
│   ├── app.py                      # FastAPI application
│   ├── config.py                   # Configuration
│   ├── requirements.txt            # Python dependencies
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── database.py            # DB connection
│   │   └── schemas.py             # Pydantic schemas
│   ├── models/
│   │   ├── rfm_segmentation.py    # RFM analysis
│   │   ├── churn_predictor.py     # Churn prediction model
│   │   ├── clv_estimator.py       # CLV estimation model
│   │   └── model_trainer.py       # Model training pipeline
│   ├── services/
│   │   ├── analytics_service.py   # Analytics business logic
│   │   ├── customer_service.py    # Customer management
│   │   └── recommendation_service.py # Retention strategies
│   └── utils/
│       ├── generate_data.py       # Synthetic data generator
│       ├── data_processor.py      # Data preprocessing
│       └── export_utils.py        # Report export utilities
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── Customers/
│   │   │   ├── Analytics/
│   │   │   └── common/
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── CustomersPage.jsx
│   │   │   ├── SegmentationPage.jsx
│   │   │   ├── ChurnAnalysisPage.jsx
│   │   │   └── CLVPage.jsx
│   │   ├── services/
│   │   │   └── api.js             # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── data/
    └── customers.db               # SQLite database
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📈 ML Model Details

### RFM Segmentation

- **Algorithm**: K-Means Clustering
- **Features**: Recency, Frequency, Monetary
- **Segments**: Champions, Loyal, At Risk, Lost, etc.

### Churn Prediction

- **Algorithm**: Random Forest Classifier
- **Features**: RFM scores, transaction patterns, engagement metrics
- **Output**: Churn probability (0-1)

### CLV Estimation

- **Algorithm**: Gradient Boosting Regressor
- **Features**: Historical purchase value, frequency, recency
- **Output**: Predicted lifetime value

## 🎨 Design Philosophy

Professional corporate dashboard with:

- Clean, minimal interface
- Intuitive navigation
- Data-driven visualizations
- Responsive design
- Accessibility compliance

## 📝 License

MIT License

## 👥 Contributing

Contributions welcome! Please read our contributing guidelines.

---

Built with ❤️ for data-driven customer retention
