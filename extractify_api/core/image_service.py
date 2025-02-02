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
        # print("base64_values:", base64_values)
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
        You are an admin filling up a form with a new employee's documents.

        Instruction:
        1. Fill up the details in JSON format
        2. Do not return data from the example if not found
        3. For the 'Address' English field, convert 'ที่อยู่' from Thai to English.
        4. Remove spaces between numbers from the 'Identification Number' field in the English section
        5. Remove spaces between numbers from the 'เลขประจำตัวประชาชน' field in the Thai section

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
                "Identification Number": "1101401642141",
                "Title, First name and Last name": "Mrs. Pariyakorn Chaimart",
                "Date of Birth": "17 May 1989",
                "Address": "110/450 Soi Ramkhamhaeng 188, Min Buri Subdistrict, Min Buri District, Bangkok",
                "Card issuance date": "14 Dec 2021",
                "Card expiration date": "16 May 2030"
            }
        }

        Important Notes:
        - Ensure extracted data matches the correct language section (Thai or English).
        - If the image does not contain a piece of information, do not return placeholders.
        - Focus only on extracting structured details relevant to the example format.
        - Only return the JSON format as shown in the example.
        """
    elif document_type == "House Registration":
        # flake8: noqa
        prompt = """
        You are an admin filling up a form with a new employee's documents.

        Instruction:
        1. Fill up the details in JSON format
        2. Do not return data from the example if not found
        3. For the 'Date of Birth' English field, convert 'เกิดเมื่อ' from Thai Buddhist calendar to Gregorian calendar
        4. Remove dashes between the numbers in the 'House Registration Number', 'National Id Number' and Fathers National Id Number fields in the English section
        5. Remove dashes between the numbers in the 'เลขรหัสประจำบ้าน', 'เลขประจำตัวประชาชน', and 'เลขประจำตัวประชาชน (บิดา)' fields in the Thai section
        6. For the 'Address List' English field, convert 'รายการที่อยู่' from Thai to English.
        7. For the 'Name' English field, convert 'ชื่อ' from Thai to English.
        8. For the 'Nationality' English field, convert 'สัญชาติ' from Thai to English.
        9. For the 'Gender' English field, convert 'เพศ' from Thai to English.
        10. For the 'Status' English field, convert 'สถานภาพ' from Thai to English.
        11. For the 'Mothers Name' English field, convert 'มารดาผู้ให้กำเนิด ชื่อ' from Thai to English.
        12. For the 'Mothers Nationality' English field, convert 'สัญชาติ (มารดา)' from Thai to English.
        13. For the 'Fathers Name' English field, convert 'บิดาผู้ให้กำเนิด ชื่อ' from Thai to English.
        14. For the 'Fathers Nationality' English field, convert 'สัญชาติ (บิดา)' from Thai to English.

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
                "House Registration Number": "10140557121",
                "Registration Office": "Local Office, Ratchathewi District",
                "Address List": "69/8 Rangsit Road, Phayathai Subdistrict, Ratchathewi District, Bangkok",
                "Village Name": "-",
                "House Name": "-",
                "House Type": "House",
                "House Description": "-",
                "Date Of Assignment Of House Number": "-",
                "Name": "Mrs. Pojanee Vanapong",
                "Nationality": "Thai",
                "Gender": "Female",
                "National Id Number": "3101403484655",
                "Status": "",
                "Date Of Birth": "8 July 1960",
                "Mothers Name": "EngSiem",
                "Mothers National Id Number": "-",
                "Mothers Nationality": "Thai",
                "Fathers Name": "Wanich",
                "Fathers National Id Number": "3601000061859",
                "Fathers Nationality": "Thai",
                "From": "Civil Registration Database",
                "To": "-"
            }
        }

        Important Notes:
        - Ensure extracted data matches the correct language section (Thai or English).
        - If the image does not contain a piece of information, do not return placeholders.
        - Focus only on extracting structured details relevant to the example format.
        - Only return the JSON format as shown in the example.
        """
    elif document_type == "Bank Book":
        # flake8: noqa
        prompt = """
        You are an admin filling up a form with a new employee's documents.

        Instruction:
        1. Fill up the details in JSON format
        2. Do not return data from the example if not found
        3. For the 'Branch of Account' English field, convert 'สำนักงาน/ สาขาบัญชี' from Thai to English
        4. Remove dashes from the 'Account Number' field in the English section
        5. Remove dashes from the 'เลขที่บัญชี' field in the Thai section

        Example JSON Format:
        {
            "Thai": {
                "เลขที่บัญชี": "7442831887",
                "ชื่อบัญชี": "บจก. เอนนี่แวร์ ทู โก",
                "สำนักงาน/ สาขาบัญชี": "อนุสาวรีย์ชัยสมรภูมิ"
            },
            "English": {
                "Account Number": "7442831887",
                "Account Name": "ANYWHERE 2 GO CO., LTD.",
                "Branch of Account": "Victory Monument"
            }
        }

        Important Notes:
        - Ensure extracted data matches the correct language section (Thai or English).
        - If the image does not contain a piece of information, do not return placeholders.
        - Focus only on extracting structured details relevant to the example format.
        - Only return the JSON format as shown in the example.
        """
    elif document_type == "DBD":
        # flake8: noqa
        prompt = """
        You are an admin filling up a form with a new employee's documents.

        Instruction:
        1. Fill up the details in JSON format
        2. Do not return data from the example if not found
        3. For the 'Headquarters Address' English field, convert 'ที่อยู่สำนักงานใหญ่' from Thai to English.


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
                "Corporate Registration Date": "20 May 2020",
                "Registration Number": "0505563006676",
                "Company Name": "O.P. COSMETIC GROUP CO., LTD.",
                "Number of Directors (persons)": "1",
                "Names of Company Directors": "Mrs. Pariyakorn Chaimart",
                "Number or Names of Authorized Signatories for the Company": "One director signs and affixes the company's seal",
                "Registered Capital (baht)": "5,000,000.00",
                "Headquarters Address": "131/19, Moo 11, Narapirom Subdistrict, Bang Len District, Nakhon Pathom Province",
                "Number of Company Objectives (items)": "24",
                "Document Issue Date": "27 October 2022"
            }
        }

        Important Notes:
        - Ensure extracted data matches the correct language section (Thai or English).
        - If the image does not contain a piece of information, do not return placeholders.
        - Focus only on extracting structured details relevant to the example format.
        - Only return the JSON format as shown in the example.
        """
    elif document_type == "CM Loan":
        # flake8: noqa
        prompt = """
        You are an admin filling up a form with a new employee's documents.

        Instruction:
        1. Fill up the details in JSON format
        2. Do not return data from the example if not found
        3. For the 'Address' English field, convert 'อาศัยอยู่ที่' from Thai to English.
        4. The following fields should be extracted from the same page:
            - 'สัญญากู้เลขที่'
            - 'สัญญาฉบับนี้ทำขึ้นเมื่อวันที่'
            - 'บริษัท (ผู้กู้)'
            - 'ทะเบียนนิติบุคคลเลขที่'
        5. The following fields should be extracted from the same page:
            - 'ชื่อของผู้ให้สินเชื่อ'
            - 'วงเงินสินเชื่อ (บาท)'
            - 'วันเบิกใช้สินเชื่อ'
        6. The following fields should be extracted from the same page:
            - 'ผู้ค้ำประกัน'
            - 'วัตถุประสงค์ของสินเชื่อ'
            - 'อัตราดอกเบี้ย'
            - 'งวดดอกเบี้ย'
            - 'วันชำระคืนเงินกู้งวดสุดท้าย'
            - 'โครงสร้างการถือหุ้น'
        7. The following fields should be extracted from the same page:
            - 'บริษัท (ผู้รับเงิน)'
            - 'วันที่ (รับเงิน)'
            - 'สัญญากู้ฉบับลงวันที่'
            - 'ชื่อของผู้ให้สินเชื่อ'
            - 'จำนวนเงิน (บาท)'
        8. The following fields should be extracted from the same page:
            - 'เดือนที่ชำระ'
            - 'วันชำระคืนเงินกู้'
            - 'จำนวนที่ต้องชำระคืน (บาท)'
        9. The following fields should be extracted from the same page:
            - 'วันที่ (สัญญา)'
            - 'บริษัท (ผู้ให้กู้)'
            - 'ชื่อ-นามสกุล (ผู้ค้ำประกัน)'
            - 'บัตรประจำตัวประชาชนเลขที่'
            - 'อาศัยอยู่ที่'
            - 'บริษัท (ผู้กู้)'
            - 'สัญญากู้เลขที่'
        10. The following fields should be extracted from the same page:
            - 'วัตถุประสงค์ของเอกสารที่ค้ำประกัน'
            - 'จำนวนเงินที่ค้ำประกัน'
            - 'ระยะเวลาค้ำประกัน'

        
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
                "Loan Agreement Number (1)": "44011027",
                "Agreement Date": "March 25, 2024",
                "Company Borrower (1)": "Generation S Company Limited",
                "Registration Number": "0105554079295",

                "Name Of The Lender (1)": "Clear Match Capital Company Limited",
                "Loan Amount Baht (1)": "200,000.00",
                "Loan Disbursement Date (1)": "March 25, 2024",

                "Guarantor": "Mr. Sorasak Wongchinsrisakul",
                "Purpose Of The Loan": "The loan is to be used for repaying the crowdfunding debenture No. 66000615 of Generation S Company Limited. The condition is that the company must transfer funds to repay the aforementioned debenture in the amount of 133,801.35 THB by March 25, 2024.",
                "Interest Rate": "16% per annum",
                "Interest Installment": "1 month",
                "Final Repayment Date": "1 month from the loan drawdown date",
                "Shareholding Structure": "Mr. Sorasak Wongchinsrisakul: 32.10%",

                "Company Payee": "Generation S Company Limited",
                "Loan Disbursement Date (2)": "March 25, 2024",
                "Agreement Date (1)": "March 25, 2024",
                "Name Of The Lender (2)": "Clear Match Capital Company Limited",
                "Loan Amount Baht (2)": "200,000.00",

                "Repayment Month": "1",
                "Loan Repayment Date": "April 25, 2024",
                "Repayment Amount Baht": "202,717.81",

                "Agreement Date (2)": "March 25, 2024",
                "Name Of The Lender (3)": "Clear Match Capital Company Limited",
                "Full Name Guarantor": "Mr. Sorasak Wongchinsrisakul",
                "National Id Number": "3100602664610",
                "Address": "10/1 Soi Ramkhamhaeng 60, Yaek 7, Hua Mak, Bang Kapi, Bangkok 10240",
                "Company Borrower (2)": "Generation S Company Limited",
                "Loan Agreement Number (2)": "44011027",

                "Purpose Of Guarantee Document": "The loan under Loan Agreement No. 44011027 is to be used for repaying the crowdfunding debenture No. 66000615 of Generation S Company Limited. The condition is that the company must transfer funds to repay the aforementioned debenture in the amount of 133,801.35 THB by March 25, 2024.",
                "Guaranteed Amount": "(1) Principal Amount: Two Hundred Thousand Baht (200,000.00 THB) under the loan agreement, and (2) Interest, Penalties, Discounts, Commission Fees, Encumbrance Fees, and Other Related Charges that the borrower is or may become liable for under the financial documents, totaling no more than Two Hundred Two Thousand Seven Hundred Seventeen Baht and Eighty-One Satang (202,717.81 THB), provided payments are made on time.",
                "Guarantee Period": "The guarantee period shall not exceed 5 years from the loan drawdown date, which corresponds to March 25, 2029."
            }
        }

        Important Notes:
        - Ensure extracted data matches the correct language section (Thai or English).
        - If the image does not contain a piece of information, do not return placeholders.
        - Focus only on extracting structured details relevant to the example format.
        - Only return the JSON format as shown in the example.
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
