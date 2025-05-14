# Real Estate Management System

A FastAPI-based real estate management system for handling properties, tenants, leases, invoices, and payments.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## Project Structure

  - `app/`: Main application package
  - `config.py`: Configuration settings
  - `database.py`: Database connection
  - `models/`: SQLAlchemy models
  - `schemas/`: Pydantic models
  - `routers/`: API endpoints
  - `services/`: Business logic

# Real_Estate_Management_Endpoints
## Authentication Endpoints (auth.py)

POST /api/v1/auth/token - Login to get access token
POST /api/v1/auth/register - Register new tenant with lease
Properties Endpoints (properties.py)

GET /api/v1/properties/ - List all properties
POST /api/v1/properties/ - Create new property
GET /api/v1/properties/{property_id}/occupancy - Get property occupancy details
GET /api/v1/properties/{property_id}/units - Get property units status
## Payments Endpoints (payments.py)

GET /api/v1/payments/ - List all payments
POST /api/v1/payments/{invoice_id} - Record payment for invoice
GET /api/v1/payments/summary - Get payment summary
POST /api/v1/payments/ - Create new payment
GET /api/v1/payments/my-payments - Get current tenant's payments
POST /api/v1/payments/rent - Pay rent
## Invoices Endpoints (invoices.py)

GET /api/v1/invoices/ - List all invoices
POST /api/v1/invoices/generate-monthly - Generate monthly invoices
GET /api/v1/invoices/overdue - Get overdue invoices
Tenants Endpoints (tenants.py)

GET /api/v1/tenants/ - List all tenants
## Leases Endpoints (leases.py)

GET /api/v1/leases/ - List all leases
## Debts Endpoints (debts.py)

GET /api/v1/debts/occupied - Get occupied properties with outstanding debts
## Root Endpoint (main.py)

GET / - Welcome message

