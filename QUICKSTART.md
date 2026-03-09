# Customer Analytics Platform - Quick Start Guide

## 🚀 Quick Start (Recommended)

### Step 1: Install Backend Dependencies

```powershell
cd backend
python -m pip install -r requirements.txt
```

### Step 2: Initialize System (Generate Data & Train Models)

```powershell
python init_system.py
```

This will:

- Create the database
- Generate 1000 synthetic customers with realistic transaction data
- Train all ML models (RFM, Churn, CLV)

### Step 3: Start Backend Server

```powershell
python app.py
```

The API will be available at:

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 4: Install Frontend Dependencies & Start

Open a **new terminal** and run:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will be available at:

- **Frontend**: http://localhost:5173



## 📋 Manual Setup (Alternative)

If you prefer to set up step-by-step:

### Backend Setup

1. **Create virtual environment** (optional but recommended):

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
```

2. **Install dependencies**:

```powershell
pip install -r requirements.txt
```

3. **Generate synthetic data**:

```powershell
python utils/generate_data.py
```

4. **Start the server**:

```powershell
python app.py
```

### Frontend Setup

1. **Install dependencies**:

```powershell
cd frontend
npm install
```

2. **Start development server**:

```powershell
npm run dev
```

---

## 🎯 Features Overview

Once running, you can:

1. **Dashboard** - View overall metrics and KPIs
2. **Customers** - Browse customers, upload CSV/Excel data
3. **Segmentation** - View RFM segments and customer distribution
4. **Churn Analysis** - Identify at-risk customers
5. **Customer Value** - See CLV predictions
6. **Recommendations** - Get AI-powered retention strategies

---

## 📊 Using Your Own Data

### Option 1: Upload via UI

1. Go to the **Customers** page
2. Click **Upload Data**
3. Select your CSV/Excel file

### Option 2: API Upload

```powershell
curl -X POST "http://localhost:8000/api/customers/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_data.csv"
```

### Required CSV Format

**For Customers:**

```csv
customer_id,name,email,phone,country,city,registration_date
CUST001,John Doe,john@example.com,+1-555-0100,United States,New York,2023-01-15
```

**For Transactions:**

```csv
transaction_id,customer_id,transaction_date,amount,quantity,product_category,product_name
TXN001,CUST001,2023-06-15,150.00,2,Electronics,Headphones
```

---

## 🔧 Training Models

### Via UI

- Go to any analytics page (Segmentation, Churn, CLV)
- Click the **Recalculate** or **Retrain Model** button

### Via API

```powershell
# Train all models
curl -X POST "http://localhost:8000/api/models/train?model_type=all"

# Train specific model
curl -X POST "http://localhost:8000/api/models/train?model_type=churn"
```

---

## 📦 Export Data

### Via UI

- Navigate to any analytics page
- Look for export buttons
- Choose format (CSV or Excel)

### Via API

```powershell
# Export customers
curl "http://localhost:8000/api/export/customers?format=csv" -o customers.csv

# Export analytics
curl "http://localhost:8000/api/export/analytics?report_type=full&format=excel" -o analytics.xlsx
```

---

## 🐛 Troubleshooting

### PowerShell Script Execution Error

If you see "running scripts is disabled", run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use

If port 8000 or 5173 is in use:

**Backend:**

```powershell
# Edit app.py and change the port
uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
```

**Frontend:**

```powershell
# Edit vite.config.js and change the port
server: { port: 5174 }
```

### Database Locked Error

Close any other instances of the application and try again.

### Missing Dependencies

Make sure you're in the correct directory and run:

```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 📚 API Documentation

Once the backend is running, visit:
**http://localhost:8000/docs**

This provides interactive API documentation where you can:

- View all endpoints
- Test API calls
- See request/response schemas

---

## 🎨 Customization

### Change Number of Synthetic Customers

Edit `backend/.env`:

```
SYNTHETIC_CUSTOMERS=2000
SYNTHETIC_DATE_RANGE_DAYS=365
```

Then re-run:

```powershell
python init_system.py
```

### Modify RFM Segments

Edit `backend/config.py` and adjust the `RFM_LABELS` dictionary.

### Change UI Theme

Edit `frontend/src/index.css` and modify the CSS variables in `:root`.

---

## 📈 Production Deployment

For production use:

1. **Use PostgreSQL** instead of SQLite
2. **Set DEBUG=False** in `.env`
3. **Add authentication** (JWT tokens)
4. **Use environment variables** for sensitive data
5. **Build frontend**: `npm run build`
6. **Use production WSGI server**: gunicorn or uvicorn with workers

---

## 💡 Tips

- **First time setup**: Use the Quick Start guide above
- **Regular use**: Just start backend and frontend servers
- **Retrain models**: Do this periodically as new data comes in
- **Performance**: For large datasets (>10K customers), consider PostgreSQL

---

## 🆘 Need Help?

Check the main README.md for:

- Architecture details
- Feature descriptions
- Technical specifications
- Contributing guidelines

---

**Enjoy your Customer Analytics Platform! 🎉**
