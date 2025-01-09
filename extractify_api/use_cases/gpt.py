import base64
import re

from extractify_api.core.image_service import (
    get_information_from_image,
    transform_base64_img_to_request_img,
)


def extract_text(image: str, document_type: str) -> str:
    """ """
    if image:
        try:
            print("start extract text")
            base64_image_data = re.sub("^data:image/.+;base64,", "", image)
            base64_decoded_image = base64.b64decode(base64_image_data)

            request_image, base64_value, image_format = transform_base64_img_to_request_img(
                base64_decoded_image
            )

            print("image transformed successfully")
        except Exception:
            raise Exception("Please provide valid image data.")

        try:
            print("start text extraction")
            image_information = get_information_from_image(
                base64_value, image_format, document_type
            )

            print("text extraction successful")
            print("image_information:", image_information)

        except Exception as error:
            print(f"Error: {error}")
            raise Exception(str(error))

    return image_information
