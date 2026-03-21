<div align="center">

# 🎯 Customer Segmentation & Retention Analytics Platform

**A production-ready, end-to-end analytics platform for customer behavior analysis, churn prediction, and AI-driven retention strategies.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-latest-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[📖 Overview](#-overview) • [✨ Features](#-features) • [🛠️ Tech Stack](#️-tech-stack) • [🚀 Quick Start](#-quick-start) • [📡 API Reference](#-api-reference) • [🧠 ML Models](#-ml-models) • [📂 Project Structure](#-project-structure)

</div>

---

## 📌 Overview

The **Customer Segmentation & Retention Analytics Platform** helps businesses unlock actionable insights from their customer data. It combines classical RFM analysis with modern machine learning to identify at-risk customers, predict lifetime value, and recommend targeted retention strategies — all through an intuitive web dashboard.

> Built with FastAPI on the backend, React on the frontend, and scikit-learn powering the ML pipeline.

---

## ✨ Features

### 📊 Core Analytics

| Feature                  | Description                                                 |
| ------------------------ | ----------------------------------------------------------- |
| **RFM Segmentation**     | Classifies customers by Recency, Frequency & Monetary value |
| **Churn Prediction**     | ML-based probability scoring for customer churn             |
| **CLV Estimation**       | Predictive Customer Lifetime Value using gradient boosting  |
| **Retention Strategies** | AI-driven, segment-specific actionable recommendations      |

### 🗄️ Data Management

- ✅ Synthetic data generation for demos & testing
- ✅ CSV / Excel file upload support
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Export reports as PDF, CSV, or Excel

### 📈 Dashboard

- Real-time analytics visualizations with interactive charts
- Customer segment comparison views & drill-down capabilities
- Responsive design for all screen sizes
- Export & sharing functionality

---

## 🛠️ Tech Stack

<table>
  <tr>
    <td valign="top" width="33%">

**Backend**

- 🐍 FastAPI (Python 3.9+)
- 🗃️ SQLAlchemy + SQLite
- 📄 Pydantic schemas
- 🔌 RESTful API + OpenAPI docs

    </td>
    <td valign="top" width="33%">

**Frontend**

- ⚛️ React 18+ with Vite
- 🎨 Material-UI / Ant Design
- 📊 Recharts
- 🔄 React Query + Context API

    </td>
    <td valign="top" width="33%">

**ML / Analytics**

- 🤖 scikit-learn
- 🐼 pandas + NumPy
- 🌲 Random Forest (Churn)
- 🚀 Gradient Boosting (CLV)

      </td>

    </tr>
  </table>

---

## � Quick Start

### Prerequisites

Ensure you have the following installed:

| Tool       | Version |
| ---------- | ------- |
| Python     | 3.9+    |
| Node.js    | 16+     |
| npm / yarn | latest  |

### 1️⃣ Backend Setup

```bash
cd backend
python -m venv venv

# Activate virtual environment
source venv/bin/activate        # macOS / Linux
# OR
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 2️⃣ Initialize the System & Generate Demo Data

```bash
python utils/generate_data.py
```

### 3️⃣ Start the Backend Server

```bash
uvicorn app:app --reload
```

> 📌 API will be available at **http://localhost:8000**
> 📘 Interactive API docs at **http://localhost:8000/docs**

### 4️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

> 🌐 App will be available at **http://localhost:5173**

---

## � API Reference

### 👤 Customer Management

| Method | Endpoint                | Description                      |
| ------ | ----------------------- | -------------------------------- |
| `GET`  | `/api/customers`        | List all customers               |
| `POST` | `/api/customers/upload` | Upload customer data (CSV/Excel) |
| `GET`  | `/api/customers/{id}`   | Get customer details             |

### 📊 Analytics

| Method | Endpoint                   | Description                       |
| ------ | -------------------------- | --------------------------------- |
| `GET`  | `/api/analytics/rfm`       | RFM segmentation analysis         |
| `GET`  | `/api/analytics/churn`     | Churn prediction results          |
| `GET`  | `/api/analytics/clv`       | Customer lifetime value estimates |
| `GET`  | `/api/analytics/dashboard` | Dashboard summary metrics         |

### 🤖 ML Models

| Method | Endpoint                  | Description                   |
| ------ | ------------------------- | ----------------------------- |
| `POST` | `/api/models/train`       | Train / retrain ML models     |
| `GET`  | `/api/models/performance` | Model performance metrics     |
| `POST` | `/api/predictions/churn`  | Predict churn for customer(s) |
| `POST` | `/api/predictions/clv`    | Predict CLV for customer(s)   |

### 📄 Reports

| Method | Endpoint               | Description                            |
| ------ | ---------------------- | -------------------------------------- |
| `GET`  | `/api/reports/export`  | Export analytics reports               |
| `GET`  | `/api/recommendations` | Get retention strategy recommendations |

---

## 🧠 ML Models

### 🔵 RFM Segmentation

- **Algorithm**: K-Means Clustering
- **Features**: Recency, Frequency, Monetary value
- **Output Segments**: Champions · Loyal · Potential Loyalists · At Risk · Lost

### 🔴 Churn Prediction

- **Algorithm**: Random Forest Classifier
- **Features**: RFM scores, transaction patterns, engagement metrics
- **Output**: Churn probability score (0 → 1)

### 🟢 CLV Estimation

- **Algorithm**: Gradient Boosting Regressor
- **Features**: Historical purchase value, frequency, recency
- **Output**: Predicted customer lifetime value (₹)

---

## 📂 Project Structure

```
customer-analytics-platform/
│
├── 📁 backend/
│   ├── app.py                          # FastAPI application entry point
│   ├── config.py                       # App configuration
│   ├── requirements.txt                # Python dependencies
│   │
│   ├── 📁 database/
│   │   ├── models.py                   # SQLAlchemy ORM models
│   │   ├── database.py                 # DB connection & session
│   │   └── schemas.py                  # Pydantic request/response schemas
│   │
│   ├── 📁 models/
│   │   ├── rfm_segmentation.py         # RFM analysis logic
│   │   ├── churn_predictor.py          # Churn prediction model
│   │   ├── clv_estimator.py            # CLV estimation model
│   │   └── model_trainer.py            # Training pipeline
│   │
│   ├── 📁 services/
│   │   ├── analytics_service.py        # Analytics business logic
│   │   ├── customer_service.py         # Customer management
│   │   └── recommendation_service.py   # Retention strategy engine
│   │
│   └── 📁 utils/
│       ├── generate_data.py            # Synthetic data generator
│       ├── data_processor.py           # Data preprocessing
│       └── export_utils.py             # Report export (PDF/CSV/Excel)
│
├── 📁 frontend/
│   └── src/
│       ├── 📁 components/
│       │   ├── Dashboard/
│       │   ├── Customers/
│       │   ├── Analytics/
│       │   └── common/
│       ├── 📁 pages/
│       │   ├── DashboardPage.jsx
│       │   ├── CustomersPage.jsx
│       │   ├── SegmentationPage.jsx
│       │   ├── ChurnAnalysisPage.jsx
│       │   └── CLVPage.jsx
│       ├── 📁 services/
│       │   └── api.js                  # Axios API client
│       ├── App.jsx
│       └── main.jsx
│
├── 📁 data/
│   └── customers.db                    # SQLite database
│
├── README.md
├── PROJECT_OVERVIEW.md
├── QUICKSTART.md
└── .gitignore
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📝 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👥 Contributing

Contributions are welcome! Please open an issue or a pull request.

---

<div align="center">

Built with ❤️ for data-driven customer retention

⭐ Star this repo if you find it useful!

</div>
