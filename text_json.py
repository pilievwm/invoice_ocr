import os
import json
import openai
from dotenv import load_dotenv
from inv_vision import extract_text_from_pdf, extract_text_from_image

load_dotenv()

def process_pdf(file_path):

    openai.api_key = os.environ['OPENAI_API_KEY']

    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension == '.pdf':
        pdf_text = extract_text_from_pdf(file_path)
    elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.tiff']:
        # if it is an image, process it as such
        pdf_text = extract_text_from_image(file_path)
    else:
        # if it is neither a PDF nor an image, stop the process
        print(f"Unsupported file format: {file_extension}")
        return None

 
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Invoice data: {pdf_text}"},
                {"role": "user", "content": "Provided is an unstructured text that is extracted from an invoice. Do not hallucinate, and use only the provided information! I would like to find the appropriate fields and add them into a valid JSON structure (make sure that comma is not missing between elements in a list or between key-value pairs in a dictionary). I want to extract from the invoice the following information: 1. type (it could be invoice or proforma or receipt or anything like that) 2. invoice_id (It could start with № or # or No. or anything that indicates that this is a number. You must include all digits, even if the number starts with 0. You are not allowed to change the data provided by the OCR. You must not confuse it with the company registration number) 3. creation_date (convert it in dd.mm.yyyy format) 4. taxable_event_date (convert it in dd.mm.yyyy format) 5. receiver (object) 5.1. name (search for CloudCart or КлаудКарт or similar) 5.2. address 5.3. company_id (This is not the VAT number. It's also known as EIK or ЕИК or Булстат or any number that refers to a company registration identifier. It usually doesn't start with the country prefix. For example, a company_id might look like 2023040323, but it never contains country ISO code as prefix. If you can not find company_id, leave it empty!) 5.4. vat_number (This usually starts with the ISO code of the country. For example: (UK): GB999 9999 73 or GBGD999 or GBHA999, (DE): DE999999999, (FR): FRKK 999999999, (ES): ESB99999999, (IT): IT99999999999, (BE): BE0999999999, (NL): NL999999999B99, (DK): DK99 99 99 99, (IE): IE9S99999L or IE9999999WI, (PT): PT999999999, (PL): PL9999999999, (SE): SE999999999999, (FI): FI99999999, (AT): ATU99999999, (EL): EL999999999, (CZ): CZ99999999 or CZ999999999 or CZ9999999999, (SK): SK9999999999, (EE): EE999999999, (HU): HU99999999, (LT): LT999999999 or LT999999999999, (LV): LV99999999999, (LU): LU9999999, (CY): CY99999999L, (MT): MT99999999, (SI): SI99999999, (BG): BG999999999 or BG9999999999, (RO): RO999999999, (HR): HR99999999999 In the United States, there is no VAT system, but there is a similar concept known as sales tax. Businesses are identified by their EIN (Employer Identification Number), which is formatted like 99-9999999. In Canada, businesses use a GST/HST number, which is formatted like 999999999RT0001. Please remember that these are formats and the actual number will vary based on each company. It could also be labeled as ДДС, ДДС номер, VAT, VAT id, TAX, TAX id, or something similar. This differs from the company_id, and they should not be confused.) 6. supplier (object) 6.1. name (Usually, it is a company name. It should contain AD or OOD or Ltd. or GMBH or ООД or АД or ЕООД) 6.2. address 6.3. company_id (This is not the VAT number. It's also known as EIK or ЕИК or Булстат or any number that refers to a company registration identifier. It usually doesn't start with the country prefix. For example, a company_id might look like 2023040323, but it never contains country ISO code as prefix. If you can not find company_id, leave it empty!) 6.4. vat_number (This usually starts with the ISO code of the country. For example: (UK): GB999 9999 73 or GBGD999 or GBHA999, (DE): DE999999999, (FR): FRKK 999999999, (ES): ESB99999999, (IT): IT99999999999, (BE): BE0999999999, (NL): NL999999999B99, (DK): DK99 99 99 99, (IE): IE9S99999L or IE9999999WI, (PT): PT999999999, (PL): PL9999999999, (SE): SE999999999999, (FI): FI99999999, (AT): ATU99999999, (EL): EL999999999, (CZ): CZ99999999 or CZ999999999 or CZ9999999999, (SK): SK9999999999, (EE): EE999999999, (HU): HU99999999, (LT): LT999999999 or LT999999999999, (LV): LV99999999999, (LU): LU9999999, (CY): CY99999999L, (MT): MT99999999, (SI): SI99999999, (BG): BG999999999 or BG9999999999, (RO): RO999999999, (HR): HR99999999999 In the United States, there is no VAT system, but there is a similar concept known as sales tax. Businesses are identified by their EIN (Employer Identification Number), which is formatted like 99-9999999. In Canada, businesses use a GST/HST number, which is formatted like 999999999RT0001. Please remember that these are formats and the actual number will vary based on each company. It could also be labeled as ДДС, ДДС номер VAT, VAT id, TAX, TAX id, or something similar. This differs from the company_id, and they should not be confused) 6.5.  accountable_person a.k.a. (MOL or М.О.Л. or МОЛ) 7. currency (Gues it from the amounts at the text. Usually it is lv. лв. USD, $, EUR. I need it in ISO 4217 format) 8. items (object [here I would like to include all lines of purchased products into an object of arrays. Each array is one row of item]) 8.1. description 8.2. quantity 8.3. unit_price (only digits) 8.4. line_price (only digits) 9. subtotal (only digits) 10. vat_total (only digits) 11. discount (if applied. It could be an amount but use only digits or percent) 12. total (only digits) 13. payment_method (Use only one of: Bank, Cash, Credit/Debit card. Search for any reference in the text. If there is a reference for card number example Master 5445********9770 or VISA 4424 **** **** 3244 use Credit/Debit card) 14. bank (Search for the bank's name where the payment should be made) 15. iban (Remove the trailing spaces from the IBAN) 16. status (if the payment method is credit or debit card or Cash, the status will be Paid else, Unpaid)"},
            ],
            temperature=0
        )
    except openai.error.APIError as e:
        print(f"OpenAI API returned an API Error: {e}")
    except openai.error.APIConnectionError as e:
        print(f"Failed to connect to OpenAI API: {e}")
    except openai.error.RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")

    output = response.choices[0].message['content']

    # Convert the output string to a Python dictionary
    output_dict = {}

    try:
        output_dict = json.loads(output)
    except json.decoder.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Invalid JSON data: {output}")


    # Get the usage information
    usage = response['usage']
    prompt_tokens = usage['prompt_tokens']
    completion_tokens = usage['completion_tokens']
    total_tokens = usage['total_tokens']

    if output_dict.get("iban"):
        output_dict["iban"] = output_dict["iban"].replace(" ", "")

    # Add the usage information to the output dictionary
    output_dict['service_information'] = {
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': total_tokens
    }

    # If you need to convert the output back to a JSON string:
    
    output_json = json.dumps(output_dict, ensure_ascii=False)
    
    invoice_id = output_dict.get("invoice_id", None)

    json_file_path = os.path.join("data", os.path.basename(invoice_id) + ".json")
    with open(json_file_path, 'w', encoding='utf-8') as f:
        f.write(output_json)
    return output_json, invoice_id
    
if __name__ == "__main__":
    import sys
    output_json, invoice_id = process_pdf(sys.argv[1])
    print(process_pdf(sys.argv[1]))