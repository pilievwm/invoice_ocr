import os
from google.cloud import vision
from pdf2image import convert_from_path
import io
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_image(image_path):
    client = vision.ImageAnnotatorClient.from_service_account_json(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations

    all_text = ""

    if texts:
        all_text += texts[0].description

    return all_text

def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path, dpi=300)

    all_text = ""

    for i, img in enumerate(images):
        # Define your output path
        output_path = os.path.join('data', f'output_{i}.jpg')
        img.save(output_path, 'JPEG')

        text = extract_text_from_image(output_path)
        all_text += text

        # Delete the image file after processing
        if os.path.isfile(output_path):
            os.remove(output_path)
        else:
            print(f"The file {output_path} does not exist")

    return all_text
