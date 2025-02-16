# Invoice Validator

This project provides a tool to validate PDF invoices by:
- Extracting prices from PDF invoices
- Verifying if the sum of product prices matches the total price
- Validating invoice dates
- Providing a user-friendly interface for file upload and validation results

## Project Structure
- `frontend/` - React.js frontend application
- `backend/` - Python FastAPI backend application

## Setup Instructions

### Backend Setup
1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Run the backend server:
```bash
uvicorn main:app --reload
```

### Frontend Setup
1. Install dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm start
```

## Technologies Used
- Frontend: React.js, Material-UI
- Backend: Python, FastAPI, PyPDF2
- PDF Processing: PyPDF2, regex 