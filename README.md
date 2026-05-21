# cocoa-ppi-dashboard

A full-stack data visualization project that processes economic indicators (Cocoa Prices and Producer Price Index) using an ETL pipeline, a Flask API, and a React frontend with PostgreSQL as the database.

🚀 Tech Stack
Backend
Python 3.10+
Flask
SQLAlchemy
PostgreSQL
Pandas
bcrypt
PyJWT
python-dotenv
flask-cors
ETL
Python
Pandas
SQLAlchemy
PostgreSQL

Frontend
React (Create React App)
Axios
React Router DOM
Recharts


Make sure you have installed:

Python 3.10+
Node.js 16+
PostgreSQL 12+
pip
npm
🐘 PostgreSQL Setup

Create the database:

CREATE DATABASE cocoa_db;
🔐 Backend Configuration (.env)

Create a .env file inside backend/:

DB_TYPE=postgres
DB_HOST=localhost
DB_PORT=
DB_NAME=cocoa_db
DB_USER=
DB_PASSWORD=

TOKEN_TTL_H=8
📦 Installation
1️⃣ Clone repository
git clone https://github.com/Andrianalyfanny/cocoa-ppi-dashboard.git
cd cocoa-ppi-dashboard
2️⃣ Install Python dependencies
pip install -r requirements.txt
3️⃣ Run ETL pipeline
python etl/pipeline.py

✔ Extracts data from CSV files
✔ Transforms data (yearly indicators)
✔ Loads data into PostgreSQL
✔ Creates default admin user

4️⃣ Start backend API
python backend/app.py

API runs on:

http://localhost:5000
5️⃣ Frontend setup

Create .env inside frontend/:

REACT_APP_API_URL=http://localhost:5000/api
6️⃣ Install frontend dependencies
cd frontend
npm install
7️⃣ Run frontend
npm start

Frontend runs on:

http://localhost:3000
🔐 Default Login

Automatically created by ETL pipeline:

Username: admin
Password: admin123
📊 Features
🔐 Authentication
JWT-based login system
Password hashing with bcrypt
📈 Dashboard Table

Displays yearly indicators:

Cocoa
Cocoa Price
Cocoa Price Change
Cocoa % Change
PPI
PPI
PPI Change
PPI % Change
PPI Reference % Change
📉 Visualizations
Cocoa price trend (line chart)
PPI trend (line chart)
Combined Cocoa vs PPI chart (line + bar)
🔄 ETL Pipeline

The ETL process:

Extracts data from CSV sources (FRED datasets)
Filters data from 2020 → 2026
Aggregates monthly → yearly values
Computes:
YoY change
YoY % change
Reference % change (PPI base 100)
Loads into PostgreSQL

🧪 API Endpoints
Auth
Login
POST /api/auth/login
Request
{
  "username": "admin",
  "password": "admin123"
}
Data
Yearly indicators
GET /api/indicators/yearly
Monthly data
GET /api/indicators/monthly
