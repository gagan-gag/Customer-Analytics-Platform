<div align="center">

# 🎯 Customer Segmentation & Retention Analytics Platform

**A production-ready, end-to-end analytics platform for customer behavior analysis, RFM segmentation, ML-powered churn prediction, CLV estimation, and AI-driven retention strategies.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.3%2B-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-latest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[📖 Overview](#-overview) • [✨ Features](#-features) • [🛠️ Tech Stack](#️-tech-stack) • [🚀 Quick Start](#-quick-start) • [📡 API Reference](#-api-reference) • [🧠 ML Models](#-ml-models) • [📂 Project Structure](#-project-structure)

</div>

---

## 📌 Overview

The **Customer Segmentation & Retention Analytics Platform** enables businesses to extract actionable insights from raw customer transaction data. By combining Recency-Frequency-Monetary (RFM) segmentation with supervised machine learning (Random Forest for churn, Gradient Boosting for CLV), the platform helps pinpoint high-risk churn candidates, estimate customer lifetime value, and serve segment-specific retention recommendations via an interactive web dashboard.

> Powered by **FastAPI** on the backend, **React + Vite** on the frontend, and **scikit-learn** for machine learning pipelines.

---

## ✨ Features

### 📊 Core Analytics
| Feature | Description |
| ------- | ----------- |
| **RFM Segmentation** | Classifies customers into 11 behavior segments based on Recency, Frequency & Monetary scores |
| **Churn Prediction** | Machine learning classification model predicting customer churn probability and risk levels |
| **CLV Estimation** | Predictive Customer Lifetime Value model using Gradient Boosting Regression |
| **Retention Recommendations** | Segment-specific and customer-level retention strategies and prioritized action plans |

### 🗄️ Data Management
- ✅ Upload customer & transaction data via CSV or Excel spreadsheets
- ✅ Automatic database initialization & seed synthetic data generator
- ✅ Complete dataset reset utility via API
- ✅ Export reporting data in CSV or Excel format

### 📈 Interactive Frontend Dashboard
- Real-time KPI summaries and interactive visual charts (Recharts)
- Page views for Dashboard, Customers, RFM Segmentation, Churn Analysis, CLV Estimation, and Recommendations
- Filter, sort, and drill-down into customer profiles and risk factors

---

## 🛠️ Tech Stack

<table>
  <tr>
    <td valign="top" width="33%">

**Backend**

- 🐍 FastAPI (Python 3.9+)
- 🗃️ SQLAlchemy ORM + SQLite
- 📄 Pydantic schemas & settings
- 🔌 RESTful API + OpenAPI (`/docs`)

    </td>
    <td valign="top" width="33%">

**Frontend**

- ⚛️ React 18 + Vite
- 🔄 TanStack React Query
- 📊 Recharts & Lucide Icons
- 🎨 Responsive CSS Design System

    </td>
    <td valign="top" width="33%">

**ML / Analytics**

- 🤖 scikit-learn & Joblib
- 🐼 pandas, NumPy, SciPy
- 🌲 Random Forest Classifier (Churn)
- 🚀 Gradient Boosting Regressor (CLV)
- 🔵 K-Means / Rule-Based RFM Scoring

    </td>
  </tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

| Tool | Recommended Version |
| ---- | ------------------- |
| Python | 3.9+ |
| Node.js | 18+ |
| npm | 9+ |

> 💡 **Windows PowerShell Tip:** If script execution is disabled on PowerShell (`UnauthorizedAccess`), run:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
> ```

---

### 1️⃣ Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate.ps1

# Install Python dependencies
python -m pip install -r requirements.txt

# If the pip launcher fails, use the Python module directly instead:
# python -m pip install -r requirements.txt
```

### 2️⃣ Initialize Database & Generate Synthetic Data

```bash
# Seed database with initial customer & transaction data
python init_system.py
```
*(Or generate synthetic data via `python utils/generate_data.py`)*

### 3️⃣ Run Backend API Server

```bash
python -m uvicorn app:app --reload
```

- 📌 **API Base URL:** [http://localhost:8000](http://localhost:8000)
- 📘 **Swagger UI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

### 4️⃣ Frontend Setup

In a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```

- 🌐 **Web Dashboard:** [http://localhost:5173](http://localhost:5173)

---

## 📡 API Reference

### 👤 Customer Management
| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `GET` | `/api/customers` | List all customers (supports `skip` & `limit`) |
| `GET` | `/api/customers/{customer_id}` | Detailed analytics for a specific customer |
| `POST` | `/api/customers/upload` | Upload customer & transaction data (CSV/Excel) |

### 📊 Analytics & Reporting
| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `GET` | `/api/analytics/dashboard` | Summary dashboard KPIs and segment metrics |
| `GET` | `/api/analytics/rfm` | Detailed RFM segmentation results |
| `GET` | `/api/analytics/rfm/segments` | RFM segment breakdown summary |
| `GET` | `/api/analytics/churn` | Detailed churn prediction analysis |
| `GET` | `/api/analytics/churn/summary` | Churn risk distributions and summary |
| `GET` | `/api/analytics/clv` | Customer Lifetime Value estimates |
| `GET` | `/api/analytics/clv/summary` | CLV segment distribution summary |

### 🤖 ML Models
| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `POST` | `/api/models/train` | Train or retrain models (`rfm`, `churn`, `clv`, or `all`) |
| `GET` | `/api/models/performance` | Retrieve ML model accuracy and performance metrics |

### 💡 Recommendations & Export
| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| `GET` | `/api/recommendations` | Customer-specific retention recommendations |
| `GET` | `/api/recommendations/strategies` | Retention strategies mapped by RFM segment |
| `GET` | `/api/recommendations/customer/{customer_id}` | Recommendation for a single customer |
| `GET` | `/api/export/customers` | Export customer records (`csv` / `excel`) |
| `GET` | `/api/export/analytics` | Export full analytics reports (`csv` / `excel`) |
| `DELETE` | `/api/data/reset` | Reset and clear database tables |

---

## 🧠 ML Models

### 🔵 RFM Segmentation
- **Logic:** Quintile-based scoring (1–5) across Recency, Frequency, and Monetary value.
- **Segments:** *Champions*, *Loyal Customers*, *Potential Loyalists*, *New Customers*, *Promising*, *Need Attention*, *About to Sleep*, *At Risk*, *Cannot Lose Them*, *Hibernating*, *Lost*.

### 🔴 Churn Prediction
- **Algorithm:** Random Forest Classifier
- **Features:** Recency, frequency, monetary metrics, average order value, purchase intervals, tenure.
- **Outputs:** Churn probability (0.0 to 1.0) and Risk Rating (*Low*, *Medium*, *High*).

### 🟢 CLV Estimation
- **Algorithm:** Gradient Boosting Regressor
- **Features:** Historical revenue, transaction frequency, recency, order trends.
- **Outputs:** Predicted 12-month Customer Lifetime Value in currency and CLV tier (*High*, *Medium*, *Low*).

---

## 📂 Project Structure

```
Customer Analytics Platform/
│
├── 📁 backend/
│   ├── app.py                          # FastAPI application entry point & routes
│   ├── config.py                       # Application configuration & settings
│   ├── init_system.py                  # Initial DB setup script
│   ├── check_db.py                     # Database verification utility
│   ├── requirements.txt                # Python dependencies
│   │
│   ├── 📁 database/
│   │   ├── database.py                 # SQLAlchemy DB session & engine setup
│   │   ├── models.py                   # ORM models (Customer, Transaction, RFM, Churn, CLV)
│   │   └── schemas.py                  # Pydantic validation schemas
│   │
│   ├── 📁 models/
│   │   ├── rfm_segmentation.py         # RFM engine and strategy rules
│   │   ├── churn_predictor.py          # Random Forest churn model engine
│   │   ├── clv_estimator.py            # Gradient Boosting CLV model engine
│   │   └── 📁 saved_models/            # Serialized trained model files (.joblib)
│   │
│   ├── 📁 services/
│   │   ├── analytics_service.py        # Core analytics calculation logic
│   │   ├── customer_service.py         # Customer CRUD & data ingestion logic
│   │   └── recommendation_service.py   # Recommendation generation service
│   │
│   └── 📁 utils/
│       ├── generate_data.py            # Synthetic dataset generator
│       └── create_datasets.py          # Dataset creation utilities
│
├── 📁 frontend/
│   ├── index.html                      # HTML entry point
│   ├── package.json                    # Frontend dependencies & scripts
│   ├── vite.config.js                  # Vite configuration
│   └── 📁 src/
│       ├── App.jsx                     # Application layout & routes setup
│       ├── main.jsx                    # React root entry
│       ├── index.css                   # Global styling system
│       │
│       ├── 📁 pages/
│       │   ├── DashboardPage.jsx       # Executive summary & overall KPIs
│       │   ├── CustomersPage.jsx       # Customer directory & file upload
│       │   ├── SegmentationPage.jsx    # RFM segmentation view
│       │   ├── ChurnAnalysisPage.jsx   # Churn risk scoring & analytics
│       │   ├── CLVPage.jsx             # CLV prediction breakdown
│       │   └── RecommendationsPage.jsx # Retention strategies & recommendations
│       │
│       └── 📁 services/
│           └── api.js                  # Axios API client setup
│
├── 📁 data/                            # SQLite database storage directory
├── README.md                           # Main documentation
├── QUICKSTART.md                       # Quick start guide
└── PROJECT_OVERVIEW.md                 # Detailed project overview
```

---

## 🧪 Testing

```bash
# Backend unit & endpoint tests
cd backend
pytest

# Frontend build check
cd frontend
npm run build
```

---

## 📝 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ for data-driven customer intelligence & retention strategy.

⭐ Star this repository if you found it helpful!

</div>
