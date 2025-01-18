import base64
import os
from io import BytesIO
from typing import Tuple

import vertexai
from langchain_core.messages import HumanMessage
from langchain_google_vertexai import ChatVertexAI
from pdf2image import convert_from_bytes
from PIL import Image

GOOGLE_PROJECT_NAME = os.environ.get("GOOGLE_PROJECT_NAME")
GOOGLE_VERTEX_AI_LOCATION = os.environ.get("GOOGLE_VERTEX_AI_LOCATION")


def transform_base64_img_to_request_img(
    base64_decoded_image: bytes, file_format: str
) -> Tuple[str, str]:
    """
    Transform a decoded Base64 image or PDF into a request-friendly format.
    Converts the image to JPEG and re-encodes it as Base64.
    """
    if file_format.lower() == "pdf":
        base64_values = []
        # Convert PDF to images
        images = convert_from_bytes(base64_decoded_image)
        if not images:
            raise ValueError("No images found in the PDF file.")

        for image in images:
            # Ensure the image is in RGB mode
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Convert the image to JPEG format
            output_buffered = BytesIO()
            image.save(output_buffered, format="JPEG")
            output_buffered.seek(0)  # Reset buffer position for subsequent reads

            # Re-encode the image as Base64
            base64_value = base64.b64encode(output_buffered.getvalue()).decode("utf-8")
            base64_values.append(base64_value)

            # Clean up the buffer to avoid potential memory issues
            output_buffered.close()
        print("base64_values:", base64_values)
    else:
        # Open the image using PIL
        pil_image = Image.open(BytesIO(base64_decoded_image))

        # Ensure the image is in RGB mode
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Convert the image to JPEG format
        output_buffered = BytesIO()
        pil_image.save(output_buffered, format="JPEG")
        output_buffered.seek(0)  # Reset buffer position for subsequent reads

        # Re-encode the image as Base64
        base64_values = [base64.b64encode(output_buffered.getvalue()).decode("utf-8")]

    request_image_format = "jpg"

    return base64_values, request_image_format


def get_information_from_image(base64_images, image_format, document_type) -> str:
    """"""
    vertexai.init(project=GOOGLE_PROJECT_NAME, location=GOOGLE_VERTEX_AI_LOCATION)
    if document_type == "ID Card":
        # flake8: noqa
        prompt = """
        You are an admin filling up the form with the new employee documents.

        Instruction:
        1. Fill up the details into the JSON format
        2. Do not return data from the example if not found

        Example JSON Format:
        {
            "Thai": {
                "เลขประจำตัวประชาชน": "1101401642141",
                "ชื่อตัวและชื่อสกุล": "นาง ปริยากร ไชยมาตร",
                "เกิดวันที่": "17 พ.ค. 2532",
                "ที่อยู่": "110/450 ซ.รามคำแหง 188 แขวงมีนบุรี เขตมีนบุรี กรุงเทพมหานคร",
                "วันออกบัตร": "14 ธ.ค. 2564",
                "วันบัตรหมดอายุ": "16 พ.ค. 2573"
            },
            "English": {
                "identification_number": "1101401642141",
                "title_first_name_last_name": "Mrs. Pariyakorn Chaimart",
                "date_of_birth": "17 May 1989",
                "address": "110/450 Soi Ramkhamhaeng 188, Min Buri Subdistrict, Min Buri District, Bangkok",
                "card_issuance_date": "14 Dec 2021",
                "card_expiration_date": "16 May 2030"
            }
        }

        Important Notes:
        - Ensure extracted data matches the correct language section (Thai or English).
        - If the image does not contain a piece of information, do not return placeholders.
        - Focus only on extracting structured details relevant to the example format.
        """
    elif document_type == "House Registration":
        # flake8: noqa
        prompt = """
        You are an admin filling up the form with the new employee documents.

        Instruction:
        1. Fill up the details into the JSON format
        2. Do not return data from the example if not found
        3. For English date_of_birth, convert from Thai Buddhist calendar to Gregorian calendar

        Example JSON Format:
        {
            "Thai": {
                "เลขรหัสประจำบ้าน": "10140557121",
                "สำนักทะเบียน": "ท้องถิ่นเขตราชเทวี",
                "รายการที่อยู่": "69/8 ถนนรางน้ำ แขวงถนนพญาไท เขตราชเทวี กรุงเทพมหานคร",
                "ชื่อหมู่บ้าน": "-",
                "ชื่อบ้าน": "-",
                "ประเภทบ้าน": "บ้าน",
                "ลักษณะบ้าน": "-",
                "วันเดือนปีที่กำหนดบ้านเลขที่": "-",
                "ชื่อ": "นาง พจนี วนาพงษ์",
                "สัญชาติ": "ไทย",
                "เพศ": "หญิง",
                "เลขประจำตัวประชาชน": "3101403484655",
                "สถานภาพ": "เจ้าบ้าน",
                "เกิดเมื่อ": "8 ก.ค. 2503",
                "มารดาผู้ให้กำเนิด ชื่อ": "เองเซี้ยม",
                "เลขประจำตัวประชาชน (มารดา)": "-",
                "สัญชาติ (มารดา)": "ไทย",
                "บิดาผู้ให้กำเนิด ชื่อ": "วนิช",
                "เลขประจำตัวประชาชน (บิดา)": "3601000061859",
                "สัญชาติ (บิดา)": "ไทย",
                "มาจาก": "ฐานข้อมูลการทะเบียนราษฎร",
                "ไปที่": "-"
            },
            "English": {
                "house_registration_number": "10140557121",
                "registration_office": "Local Office, Ratchathewi District",
                "address_list": "69/8 Rangsit Road, Phayathai Subdistrict, Ratchathewi District, Bangkok",
                "village_name": "-",
                "house_name": "-",
                "house_type": "House",
                "house_description": "-",
                "date_of_assignment_of_house_number": "-",
                "name": "Mrs. Pojanee Vanapong",
                "nationality": "Thai",
                "gender": "Female",
                "national_id_number": "3101403484655",
                "status": "",
                "date_of_birth": "8 July 1960",
                "mothers_name": "EngSiem",
                "mothers_national_id_number": "-",
                "mothers_nationality": "Thai",
                "fathers_name": "Wanich",
                "fathers_national_id_number": "3601000061859",
                "fathers_nationality": "Thai",
                "from": "Civil Registration Database",
                "to": "-"
            }
        }

        Important Notes:
        - Ensure extracted data matches the correct language section (Thai or English).
        - If the image does not contain a piece of information, do not return placeholders.
        - Focus only on extracting structured details relevant to the example format.
        """

    text_message = {
        "type": "text",
        "text": "What's in this image? provide full detail as possible. And also \n"
        + prompt.lower(),
    }
    content = [text_message]
    for base64_image in base64_images:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/{image_format};base64,{base64_image}"},
            }
        )
    message = HumanMessage(content=content)

    # models = ["gemini-pro-vision", "gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
    output = ChatVertexAI(model="gemini-1.5-flash", location="asia-southeast1").invoke([message])

    return output.content if output else ""
