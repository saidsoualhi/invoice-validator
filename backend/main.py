from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from PyPDF2 import PdfReader, PdfWriter
import re
from typing import List, Dict
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import os
import tempfile

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InvoiceValidator:
    @staticmethod
    def extract_prices(pdf_content: bytes) -> Dict:
        try:
            # Create a PDF reader object
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            # Extract invoice date and number
            date_pattern = r'Date:\s*(\d{4}-\d{2}-\d{2})'
            invoice_num_pattern = r'Invoice\s*#:\s*([^\n]+)'
            
            date_match = re.search(date_pattern, text)
            invoice_num_match = re.search(invoice_num_pattern, text)
            
            invoice_date = date_match.group(1) if date_match else None
            invoice_number = invoice_num_match.group(1) if invoice_num_match else None

            # Find all price amounts, handling comma-separated numbers
            price_pattern = r'\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            prices_text = re.findall(price_pattern, text)
            
            # Convert prices to float, removing commas
            prices = [float(price.replace('$', '').replace(',', '')) for price in prices_text]
            
            # Find the total amount (looking for "Total: $X,XXX.XX" pattern)
            total_pattern = r'Total:\s*\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            total_match = re.search(total_pattern, text)
            
            if total_match:
                total_text = re.search(price_pattern, total_match.group())
                if total_text:
                    total = float(total_text.group().replace('$', '').replace(',', ''))
                else:
                    total = prices[-1] if prices else 0
            else:
                total = prices[-1] if prices else 0
            
            # Extract item descriptions
            items_pattern = r'\d+\.\s*([^$]+)\s*\$[\d,.]+'
            items_desc = re.findall(items_pattern, text)
            
            # Remove the total and tax from the items list
            # Looking for tax amount
            tax_pattern = r'Tax[^$]*\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            tax_match = re.search(tax_pattern, text)
            if tax_match:
                tax_amount = float(re.search(price_pattern, tax_match.group()).group().replace('$', '').replace(',', ''))
            else:
                tax_amount = 0

            # Get subtotal
            subtotal_pattern = r'Subtotal:\s*\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
            subtotal_match = re.search(subtotal_pattern, text)
            if subtotal_match:
                subtotal_text = re.search(price_pattern, subtotal_match.group())
                subtotal = float(subtotal_text.group().replace('$', '').replace(',', ''))
            else:
                # If no subtotal found, calculate from items
                subtotal = sum(prices[:-2]) if len(prices) > 2 else sum(prices)

            # Filter out the total and tax from items
            items = [price for price in prices if price != total and price != tax_amount and price != subtotal]
            
            # Create items with descriptions
            items_with_desc = []
            for i, (desc, price) in enumerate(zip(items_desc, items)):
                items_with_desc.append({
                    "description": desc.strip(),
                    "price": price
                })

            # Calculate expected total
            calculated_total = subtotal + tax_amount
            
            # Perform validations
            items_sum_valid = abs(subtotal - sum(items)) < 0.01  # Check if items sum matches subtotal
            total_valid = abs(calculated_total - total) < 0.01  # Check if total matches subtotal + tax
            
            return {
                "invoice_date": invoice_date,
                "invoice_number": invoice_number,
                "items": items_with_desc,
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "total": total,
                "calculated_total": calculated_total,
                "items_sum_valid": items_sum_valid,
                "total_valid": total_valid,
                "is_valid": items_sum_valid and total_valid,
                "validation_messages": {
                    "items_sum": "Items sum matches subtotal" if items_sum_valid else "Items sum does not match subtotal",
                    "total": "Total amount is correct (subtotal + tax)" if total_valid else "Total amount should be " + str(calculated_total)
                }
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

def generate_corrected_pdf(invoice_data: Dict) -> bytes:
    # Create a BytesIO buffer for the PDF
    buffer = io.BytesIO()
    
    # Create the PDF with reportlab
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750  # Starting y position
    
    # Add invoice header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, y, "INVOICE")
    y -= 30
    
    c.setFont("Helvetica", 12)
    if invoice_data.get("invoice_date"):
        c.drawString(50, y, f"Date: {invoice_data['invoice_date']}")
    y -= 20
    
    if invoice_data.get("invoice_number"):
        c.drawString(50, y, f"Invoice #: {invoice_data['invoice_number']}")
    y -= 40
    
    # Add items header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Items:")
    y -= 20
    
    # Add items
    c.setFont("Helvetica", 12)
    for i, item in enumerate(invoice_data["items"], 1):
        c.drawString(50, y, f"{i}. {item['description']} ${item['price']:,.2f}")
        y -= 20
    
    y -= 20
    
    # Add totals
    c.drawString(50, y, f"Subtotal: ${invoice_data['subtotal']:,.2f}")
    y -= 20
    c.drawString(50, y, f"Tax (8%): ${invoice_data['tax_amount']:,.2f}")
    y -= 20
    c.drawString(50, y, "_" * 40)
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, f"Total: ${invoice_data['calculated_total']:,.2f}")
    
    c.save()
    
    # Get the value of the BytesIO buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

@app.post("/api/validate-invoice")
async def validate_invoice(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    content = await file.read()
    validator = InvoiceValidator()
    result = validator.extract_prices(content)
    
    return result

@app.post("/api/generate-correction")
async def generate_correction(invoice_data: Dict):
    try:
        pdf_bytes = generate_corrected_pdf(invoice_data)
        
        # Create a temporary file with full path
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "corrected_invoice.pdf")
        
        # Write the PDF to the temporary file
        with open(temp_path, "wb") as f:
            f.write(pdf_bytes)
        
        # Return the file
        return FileResponse(
            temp_path,
            media_type="application/pdf",
            filename="corrected_invoice.pdf",
            background=None  # Prevent background deletion
        )
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating corrected invoice: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 