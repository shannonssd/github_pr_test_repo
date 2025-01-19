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
    elif document_type == "Bank Book":
        # flake8: noqa
        prompt = """
        You are an admin filling up the form with the new employee documents.

        Instruction:
        1. Fill up the details into the JSON format
        2. Do not return data from the example if not found
        3. For the branch_of_account english field, convert 'สำนักงาน/ สาขาบัญชี' from Thai to English

        Example JSON Format:
        {
            "Thai": {
                "เลขที่บัญชี": "7442831887",
                "ชื่อบัญชี": "บจก. เอนนี่แวร์ ทู โก",
                "สำนักงาน/ สาขาบัญชี": "อนุสาวรีย์ชัยสมรภูมิ"
            },
            "English": {
                "account_number": "7442831887",
                "account_name": "ANYWHERE 2 GO CO., LTD.",
                "branch_of_account": "Victory Monument"
            }
        }

        Important Notes:
        - Ensure extracted data matches the correct language section (Thai or English).
        - If the image does not contain a piece of information, do not return placeholders.
        - Focus only on extracting structured details relevant to the example format.
        """
    elif document_type == "DBD":
        # flake8: noqa
        prompt = """
        You are an admin filling up the form with the new employee documents.

        Instruction:
        1. Fill up the details into the JSON format
        2. Do not return data from the example if not found

        Example JSON Format:
        {
            "Thai": {
                "วันที่จดทะเบียนนิติบุคคล":	"20 พฤษภาคม 2563",
                "ทะเบียนนิติบุคคลเลขที่": "0505563006676",
                "ชื่อบริษัท": "บริษัท โอ.พี. คอสเมติค กรุ๊ป จำกัด",
                "จำนวนกรรมการบริษัท (คน)": "1",
                "รายชื่อกรรมการบริษัท": "นาง ปริยากร ไชยมาคร",
                "จำนวนหรือชื่อกรรมการซึ่งลงชื่อผูกพันบริษัทได้คือ":	"กรรมการหนึ่งคนลงลายมือชื่อ และประทับตราสำคัญของบริษัท",
                "ทุนจดทะเบียน (บาท)": "5,000,000.00",
                "ที่อยู่สำนักงานใหญ่": "131/19 หมู่ที่ 11 ตำบลนราภิรมย์ อำเภอบางเลน จังหวัดนครปฐม",
                "จำนวนวัตถุประสงค์ของบริษัท (ข้อ)": "24",
                "ออกเอกสารให้ ณ วันที่": "27 เดือน ตุลาคม พ.ศ. 2565"
            },
            "English": {
                "corporate_registration_date": "20 May 2020",
                "registration_number": "0505563006676",
                "company_name": "O.P. COSMETIC GROUP CO., LTD.",
                "number_of_directors_persons": "1",
                "names_of_company_directors": "Mrs. Pariyakorn Chaimart",
                "number_or_names_of_authorized_signatories_for_the_company": "One director signs and affixes the company's seal",
                "registered_capital_baht": "5,000,000.00",
                "headquarters_address": "131/19, Moo 11, Narapirom Subdistrict, Bang Len District, Nakhon Pathom Province",
                "number_of_company_objectives_items": "24",
                "document_issue_date": "27 October 2022"
            }
        }

        Important Notes:
        - Ensure extracted data matches the correct language section (Thai or English).
        - If the image does not contain a piece of information, do not return placeholders.
        - Focus only on extracting structured details relevant to the example format.
        """
    elif document_type == "CM Loan":
        # flake8: noqa
        prompt = """
        You are an admin filling up the form with the new employee documents.

        Instruction:
        1. Fill up the details into the JSON format
        2. Do not return data from the example if not found

        Example JSON Format:
        {
            "Thai": {
                "สัญญากู้เลขที่": "44011027",
                "สัญญาฉบับนี้ทำขึ้นเมื่อวันที่": "25 มีนาคม พ.ศ. 2567",
                "บริษัท (ผู้กู้)": "เจนเนอเรชั่น เอส จำกัด",
                "ทะเบียนนิติบุคคลเลขที่": "0105554079295",

                "ชื่อของผู้ให้สินเชื่อ": "บริษัท เคลียร์ แมทช์ แคปปิตอล จำกัด",
                "วงเงินสินเชื่อ (บาท)": "200,000.00",
                "วันเบิกใช้สินเชื่อ": "25 มีนาคม พ.ศ. 2567",

                "ผู้ค้ำประกัน": "นาย สรศักดิ์ วงศ์ชินศรีสกุล",
                "วัตถุประสงค์ของสินเชื่อ": "ใช้สำหรับชำระคืนหุ้นกู้คราวด์ฟันดิงเลขที่ 66000615 ของบริษัท เจนเนอเรชั่น เอส จำกัด โดยมีเงื่อนไขคือทางบริษัทฯ จะต้องทำการโอนเงินเพื่อชำระคืนหุ้นกู้ดังกล่าว เป็นจำนวนเงิน 133,801.35 บาท ภายในวันที่ 25 มีนาคม พ.ศ. 2567",
                "อัตราดอกเบี้ย": "16% ต่อปี",
                "งวดดอกเบี้ย": "1 เดือน",
                "วันชำระคืนเงินกู้งวดสุดท้าย": "1 เดือน ถัดจากวันเบิกใช้สินเชื่อ",
                "โครงสร้างการถือหุ้น": "นาย สรศักดิ์ วงศ์ชินศรีสกุล: 32.10%",

                "บริษัท (ผู้รับเงิน)": "บริษัท เจนเนอเรชั่น เอส จำกัด",
                "วันที่ (รับเงิน)": "25 มีนาคม พ.ศ. 2567",
                "สัญญากู้ฉบับลงวันที่": "25 มีนาคม พ.ศ. 2567",
                "ชื่อของผู้ให้สินเชื่อ": "บริษัท เคลียร์ แมทช์ แคปปิตอล จำกัด",
                "จำนวนเงิน (บาท)": "200,000.00",

                "เดือนที่ชำระ": "1",
                "วันชำระคืนเงินกู้": "25 เมษายน พ.ศ. 2567",
                "จำนวนที่ต้องชำระคืน (บาท)": "202,717.81",

                "วันที่ (สัญญา)": "25 มีนาคม พ.ศ. 2567",
                "บริษัท (ผู้ให้กู้)": "บริษัท เคลียร์ แมทช์ แคปปิตอล จำกัด",
                "ชื่อ-นามสกุล (ผู้ค้ำประกัน)": "นาย สรศักดิ์ วงศ์ชินศรีสกุล",
                "บัตรประจำตัวประชาชนเลขที่": "3100602664610",
                "อาศัยอยู่ที่": "10/1 ซ.รามคำแหง 60 แยก 7 หัวหมาก บางกะปิ กรุงเทพมหานคร 10240",
                "บริษัท (ผู้กู้)": "บริษัท เจนเนอเรชั่น เอส จำกัด",
                "สัญญากู้เลขที่": "44011027",

                "วัตถุประสงค์ของเอกสารที่ค้ำประกัน": "สินเชื่อเงินกู้ภายใต้สัญญากู้เลขที่ 44011027 ใช้สำหรับชำระคืนหุ้นกู้คราวด์ฟันดิงเลขที่ 66000615 ของบริษัท เจนเนอเรชั่น เอส จำกัด โดยมีเงื่อนไขคือทางบริษัทฯ จะต้องทำการโอนเงินเพื่อชำระคืนหุ้นกู้ดังกล่าว เป็นจำนวนเงิน 133,801.35 บาท ภายในวันที่ 25 มีนาคม พ.ศ. 2567",
                "จำนวนเงินที่ค้ำประกัน": "(1) สองแสนบาทถ้วน (200,000.00 บาท) ภายใต้สัญญากู้ยืมเงิน และ (2) ดอกเบี้ยเงินกู้ ดอกเบี้ยผิดนัด ส่วนลด ค่านายหน้า ค่าภาระติดพัน และค่าใช้จ่ายต่างๆทั้งหมดที่ผู้กู้มีหรืออาจจะมีความรับผิดต่อผู้ให้กู้ ภายใต้เอกสารทางการเงินเป็นจำนวนทั้งหมดไม่เกิน สองแสนสองพันเจ็ดร้อยสิบเจ็ดบาทแปดสิบเอ็ดสตางค์ (202,717.81 บาท) ในกรณีที่ชำระเงินตรงตามที่กำหนด",
                "ระยะเวลาค้ำประกัน": "ไม่เกินกว่าระยะเวลา 5 ปี นับจากวันที่เบิกใช้เงินกู้ ซึ่งตรงกับวันที่ 25 มีนาคม พ.ศ. 2572"
            },
            "English": {
                "loan_agreement_number": "44011027",
                "agreement_date": "March 25, 2024",
                "company_borrower": "Generation S Company Limited",
                "registration_number": "0105554079295",

                "name_of_the_lender": "Clear Match Capital Company Limited",
                "loan_amount_baht": "200,000.00",
                "loan_disbursement_date": "March 25, 2024",

                "guarantor": "Mr. Sorasak Wongchinsrisakul",
                "purpose_of_the_loan": "The loan is to be used for repaying the crowdfunding debenture No. 66000615 of Generation S Company Limited. The condition is that the company must transfer funds to repay the aforementioned debenture in the amount of 133,801.35 THB by March 25, 2024.",
                "interest_rate": "16% per annum",
                "interest_installment": "1 month",
                "final_repayment_date": "1 month from the loan drawdown date",
                "shareholding_structure": "Mr. Sorasak Wongchinsrisakul: 32.10%",

                "company_payee": "Generation S Company Limited",
                "loan_disbursement_date": "March 25, 2024",
                "agreement_date": "March 25, 2024",
                "name_of_the_lender": "Clear Match Capital Company Limited",
                "loan_amount_baht": "200,000.00",

                "repayment_month": "1",
                "loan_repayment_date": "April 25, 2024",
                "repayment_amount_baht": "202,717.81",

                "agreement_date": "March 25, 2024",
                "name_of_the_lender": "Clear Match Capital Company Limited",
                "full_name_guarantor": "Mr. Sorasak Wongchinsrisakul",
                "national_id_number": "3100602664610",
                "address": "10/1 Soi Ramkhamhaeng 60, Yaek 7, Hua Mak, Bang Kapi, Bangkok 10240",
                "company_borrower": "Generation S Company Limited",
                "loan_agreement_number": "44011027",

                "purpose_of_guarantee_document": "The loan under Loan Agreement No. 44011027 is to be used for repaying the crowdfunding debenture No. 66000615 of Generation S Company Limited. The condition is that the company must transfer funds to repay the aforementioned debenture in the amount of 133,801.35 THB by March 25, 2024.",
                "guaranteed_amount": "(1) Principal Amount: Two Hundred Thousand Baht (200,000.00 THB) under the loan agreement, and (2) Interest, Penalties, Discounts, Commission Fees, Encumbrance Fees, and Other Related Charges that the borrower is or may become liable for under the financial documents, totaling no more than Two Hundred Two Thousand Seven Hundred Seventeen Baht and Eighty-One Satang (202,717.81 THB), provided payments are made on time.",
                "guarantee_period": "The guarantee period shall not exceed 5 years from the loan drawdown date, which corresponds to March 25, 2029."
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
