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
