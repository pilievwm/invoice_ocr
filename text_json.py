import os
import re
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
                {"role": "user", "content": "Provided is an unstructured text that is extracted from an invoice. Do not hallucinate, and use only the provided information! I would like to find the appropriate fields and add them into a valid JSON structure (make sure that comma is not missing between elements in a list or between key-value pairs in a dictionary). I want to extract from the invoice the following information: \n1. type (it could be invoice or proforma or receipt or anything like that) \n2. invoice_id (It could start with № or # or No. or anything that indicates that this is a number. You must include all digits, even if the number starts with 0. You are not allowed to change the data provided by the OCR. You must not confuse it with the company registration number) \n3. creation_date (convert it in dd.mm.yyyy format) \n4. taxable_event_date (convert it in dd.mm.yyyy format) \n5. receiver (object) \n5.1. name (search for CloudCart or КлаудКарт or similar) \n5.2. address \n5.3. company_id (Company ID or CID or registration number or EIK or ЕИК or Булстат. For example, a company_id might look like 2023040323, but it never contains letters like BG3402049293. If you DO NOT find company_id, leave it empty!) \n5.4. vat_number (This is the VAT ID, or VAT registration number, or this usually starts with the ISO 2 code of the country. For example: (UK): GB999 9999 73 or GBGD999 or GBHA999, (DE): DE999999999, (FR): FRKK 999999999, (ES): ESB99999999, (IT): IT99999999999, (BE): BE0999999999, (NL): NL999999999B99, (DK): DK99 99 99 99, (IE): IE9S99999L or IE9999999WI, (PT): PT999999999, (PL): PL9999999999, (SE): SE999999999999, (FI): FI99999999, (AT): ATU99999999, (EL): EL999999999, (CZ): CZ99999999 or CZ999999999 or CZ9999999999, (SK): SK9999999999, (EE): EE999999999, (HU): HU99999999, (LT): LT999999999 or LT999999999999, (LV): LV99999999999, (LU): LU9999999, (CY): CY99999999L, (MT): MT99999999, (SI): SI99999999, (BG): BG999999999 or BG9999999999, (RO): RO999999999, (HR): HR99999999999 In the United States, there is no VAT system, but there is a similar concept known as sales tax. Businesses are identified by their EIN (Employer Identification Number), which is formatted like 99-9999999. In Canada, businesses use a GST/HST number, which is formatted like 999999999RT0001. Please remember that these are formats and the actual number will vary based on each company. It could also be labeled as ДДС, ДДС номер, VAT, VAT id, TAX, TAX id, or something similar. This differs from the company_id, and they should not be confused.) \n6. supplier (object) \n6.1. name (Usually, it is a company name. It should contain AD or OOD or Ltd. or GMBH or ООД or АД or ЕООД) \n6.2. address \n6.3. company_id (Company ID or CID or registration number or EIK or ЕИК or Булстат. For example, a company_id might look like 2023040323, but it never contains letters like BG3402049293. If you DO NOT find company_id, leave it empty!) \n6.4. vat_number (This is the VAT ID, or VAT registration number, or this usually starts with the ISO code of the country. For example: (UK): GB999 9999 73 or GBGD999 or GBHA999, (DE): DE999999999, (FR): FRKK 999999999, (ES): ESB99999999, (IT): IT99999999999, (BE): BE0999999999, (NL): NL999999999B99, (DK): DK99 99 99 99, (IE): IE9S99999L or IE9999999WI, (PT): PT999999999, (PL): PL9999999999, (SE): SE999999999999, (FI): FI99999999, (AT): ATU99999999, (EL): EL999999999, (CZ): CZ99999999 or CZ999999999 or CZ9999999999, (SK): SK9999999999, (EE): EE999999999, (HU): HU99999999, (LT): LT999999999 or LT999999999999, (LV): LV99999999999, (LU): LU9999999, (CY): CY99999999L, (MT): MT99999999, (SI): SI99999999, (BG): BG999999999 or BG9999999999, (RO): RO999999999, (HR): HR99999999999 In the United States, there is no VAT system, but there is a similar concept known as sales tax. Businesses are identified by their EIN (Employer Identification Number), which is formatted like 99-9999999. In Canada, businesses use a GST/HST number, which is formatted like 999999999RT0001. Please remember that these are formats and the actual number will vary based on each company. It could also be labeled as ДДС, ДДС номер VAT, VAT id, TAX, TAX id, or something similar. This differs from the company_id, and they should not be confused) \n6.5.  accountable_person a.k.a. (MOL or М.О.Л. or МОЛ) \n7. currency (Gues it from the amounts at the text. Usually it is lv. лв. USD, $, EUR. I need it in ISO 4217 format) \n8. items (object [here I would like to include all lines of purchased products into an object of arrays. Each array is one row of item]) \n8.1. description \n8.2. quantity \n8.3. unit_price (only digits) \n8.4. line_price (only digits) \n9. subtotal (only digits) \n10. vat_total (only digits) \n11. discount (if applied. It could be an amount but use only digits or percent) \n12. total (only digits) \n13. payment_method (Use only one of: 1 (for Bank), 3 (for Cash), 2 (for Credit/Debit card). Search for any reference in the text. If there is a reference for card number example Master 5445********9770 or VISA 4424 **** **** 3244 use 2) \n14. bank (Search for the bank's name where the payment should be made) \n15. iban (Remove the trailing spaces from the IBAN) 16. status (if the payment method is Credit/Debit card or Cash, the status is 1 else, if it is Bank make it 0)"},
            ],
            temperature=0
        )

        # Extract the data for the second call
        extracted_data = response.choices[0].message['content']

        # Second API call
        response_category = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "[{\"id\":1,\"name\":\"Marketing Expenses\"},{\"id\":2,\"name\":\"Development\"},{\"id\":3,\"name\":\"Infrastructure Expenses\"},{\"id\":5,\"name\":\"Delivery Expenses\"},{\"id\":6,\"name\":\"Accounting Expenses\"},{\"id\":7,\"name\":\"Outsource services\"},{\"id\":8,\"name\":\"Domains\"},{\"id\":10,\"name\":\"Merchant\"},{\"id\":11,\"name\":\"Equipment \"},{\"id\":12,\"name\":\"Phone\"},{\"id\":13,\"name\":\"Office Expenses\"},{\"id\":14,\"name\":\"Additional Benefits Expenses\"},{\"id\":15,\"name\":\"Legal Expenses\"},{\"id\":16,\"name\":\"Equipment & Maintenance Expenses \"},{\"id\":17,\"name\":\"Copywriting\"},{\"id\":21,\"name\":\"Bonus payment\"},{\"id\":22,\"name\":\"System Administrator Fees\"},{\"id\":24,\"name\":\"Online Banking \"},{\"id\":25,\"name\":\"Resellers\"},{\"id\":26,\"name\":\"Internship Salaries\"},{\"id\":27,\"name\":\"BG \u0415ntertainment \u0415xpenses\"},{\"id\":29,\"name\":\"Others\"},{\"id\":31,\"name\":\"Business Trip Expenses\"},{\"id\":32,\"name\":\"Representation Expenses\"},{\"id\":34,\"name\":\"Sales Commission Expenses\"},{\"id\":35,\"name\":\"Ecosystem Expenses\"},{\"id\":44,\"name\":\"Food, Drinks & Snacks Expenses\"}]"},
                {"role": "user", "content": f"Select the category from the provided JSON file by using information from the purchased goods or services in the description field of the invoice. Give the selected existing category ID followed by the country code in ISO 2 format. The country code you can get from the supplier address! Example: 7, DE or 22, IT. \n\nInvoice data: {extracted_data}"},
            ],
            temperature=0
        )
        
        # After processing the second API call
        split_content = response_category.choices[0].message['content'].split(", ")

        # Check if the split operation returned two values
        if len(split_content) >= 2:
            category_id = split_content[0]
            # Join all items except the first one, which is category_id, and search for country code
            rest_of_content = ", ".join(split_content[1:])
            country_match = re.search(r'\b[A-Z]{2}\b', rest_of_content)  # \b for word boundary, [A-Z]{2} for 2 uppercase letters
            if country_match:  # If a country code is found
                country_code = country_match.group()  # Get the matched country code
            else:  # If no country code is found
                country_code = "BG"  # Use default value
        else:  # If only one value was returned, assign it to category_id and use a default value for country_code
            category_id = split_content[0]
            country_code = "BG"

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

    # Add category_id and country_code to the output_dict
    output_dict["category_id"] = category_id
    output_dict["country_code"] = country_code.strip()

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