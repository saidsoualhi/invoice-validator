# Invoice Validator

A modern web application that validates PDF invoices by performing detailed calculations and offering correction capabilities.

## Features

- **PDF Invoice Processing**
  - Extracts prices, items, and totals from PDF invoices
  - Handles comma-separated numbers and currency formats
  - Validates invoice dates and numbers

- **Comprehensive Validation**
  - Verifies individual item prices
  - Validates subtotal calculations
  - Checks tax amount accuracy
  - Confirms total amount matches (subtotal + tax)

- **Smart Correction System**
  - Generates corrected PDF invoices when discrepancies are found
  - Maintains original invoice formatting and information
  - Provides clear validation messages for each check

- **Modern User Interface**
  - Drag-and-drop file upload
  - Real-time validation feedback
  - Clear presentation of financial data
  - Responsive design for all screen sizes

## Project Structure
- `frontend/` - React.js frontend application
  - Modern Material-UI components
  - Real-time validation display
  - PDF generation integration
- `backend/` - Python FastAPI backend application
  - PDF text extraction
  - Price calculation and validation
  - PDF generation with reportlab

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
# Or use the provided batch file:
run_server.bat
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
# Or use the provided batch file:
run_frontend.bat
```

### Quick Start
Use the provided batch file to start both servers:
```bash
start_app.bat
```

## Technologies Used
- **Frontend**
  - React.js
  - Material-UI (MUI)
  - Axios for API calls
  - react-dropzone for file uploads
  
- **Backend**
  - Python 3.10+
  - FastAPI
  - PyPDF2 for PDF processing
  - reportlab for PDF generation
  - regex for text extraction

## Features in Detail

### Invoice Validation
- Extracts and validates:
  - Individual item prices and descriptions
  - Subtotal calculation
  - Tax amount (8%)
  - Total amount
  - Invoice date and number

### PDF Generation
- Generates corrected invoices with:
  - Original invoice information
  - Corrected calculations
  - Professional formatting
  - Clear item descriptions
  - Accurate totals

### User Interface
- Modern, responsive design
- Interactive upload area
- Clear validation messages
- Financial summary grid
- Easy-to-read item list
- One-click correction generation 