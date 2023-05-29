import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

CONSOLE_URL = os.getenv('CONSOLE_URL')
WEBHOOK_API_KEY = os.getenv('WEBHOOK_API_KEY')

def NewCompanyInvoice(country, cid, date, amount, currency, payment_method, payment_status, category_id, invoice_number, invoice_file, company_name, calculate_vat):
    url = CONSOLE_URL
    headers = {
        'Accept': 'application/json',
        'Webhook-Api-Key': WEBHOOK_API_KEY,
    }
    data = {
        'country': country,
        'company[cid]': cid,
        'date': date,
        'amount': amount,
        'currency': currency,
        'payment_method': payment_method,
        'payment_status': payment_status,
        'category_id': category_id,
        'invoice_number': invoice_number,
        'company[name]': company_name,
        'company[calculate_vat]': calculate_vat,
    }
    files = {'invoice_file': open(invoice_file, 'rb')}
    
    response = requests.post(url, headers=headers, data=data, files=files)
    print(response.status_code)
    return response.json()
