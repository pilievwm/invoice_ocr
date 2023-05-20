# invoice_ocr

Using Google Vision API and OpenAI GPT-3 to extract information from invoice images or PDFs. This information is then used to generate a structured JSON representation of the invoice. The extracted information includes invoice type, invoice ID, creation date, taxable event date, receiver, supplier, currency, items, etc.

Here are some points of interest about each Python file:

app.py: This file runs the main server using Flask, a lightweight web server framework for Python. It hosts a web server that listens for POST requests on the '/checkmail' route. When a request is received, it reads the message data from the request, decodes it, and passes it to check_mail_main() function. The server also has the capability to serve via HTTPS as it's using an SSL context.

inv_vision.py: This module uses Google Vision API to perform OCR on images and PDFs. The extract_text_from_image() function reads an image and returns extracted text. The extract_text_from_pdf() function first converts a PDF into images, then uses extract_text_from_image() to extract text from each page.

checkMail.py: This module authenticates with Google and checks a user's Gmail account for new messages. When it finds a new message, it marks the message as read, then processes the message's attachments. If an attachment is a file (possibly a PDF), it uses the function from text_json.py to extract invoice information from it.

text_json.py: This module uses the GPT-3 model from OpenAI to parse the text extracted from the invoice PDF or image. It uses the model to generate a JSON structure containing the relevant information about the invoice.

To run the system, you need to set several environment variables for authentication (like Google and OpenAI API keys), configuration (like Gmail user ID, topic name, webhook URL), and file paths (like token and credential paths). Make sure all these environment variables are correctly set in your .env file.

Also, you will need to ensure you have all the necessary Python libraries installed in your environment. You can use pip install <library_name> to install a library. The libraries you are using include flask, google-cloud-vision, google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client, pdf2image, openai, python-dotenv, and others.
