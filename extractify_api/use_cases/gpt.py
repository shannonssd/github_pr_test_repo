import base64
import re
import uuid
from typing import Tuple

from django.core.cache import cache
from pdf2image import convert_from_bytes

from extractify_api.core.image_service import (
    get_information_from_image,
    transform_base64_img_to_request_img,
)


def extract_text(image: str, document_type: str) -> uuid.UUID:
    """ """
    if image:
        try:
            print("start extract text")

            if image.startswith("data:application/pdf;base64"):
                base64_image_data = re.sub("^data:application/pdf;base64,", "", image)
                file_format = "pdf"
            else:
                base64_image_data = re.sub("^data:image/.+;base64,", "", image)
                file_format = "image"
            base64_decoded_image = base64.b64decode(base64_image_data)

            base64_value, image_format = transform_base64_img_to_request_img(
                base64_decoded_image, file_format
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

            # Cache data and return uuid
            key = str(uuid.uuid4())
            cache.set(f"file_format_{key}", file_format, timeout=300)
            cache.set(f"image_{key}", image, timeout=300)
            cache.set(f"image_information_{key}", image_information, timeout=300)

        except Exception as error:
            print(f"Error: {error}")
            raise Exception(str(error))

    return key


def retrieve_data(uuid: str) -> Tuple[str, str, str]:
    """ """
    file_format = cache.get(f"file_format_{uuid}")
    image = cache.get(f"image_{uuid}")
    image_information = cache.get(f"image_information_{uuid}")

    # print("retrieved_cached_image:", image)
    # print("retrieved_cached_image_information:", image_information)

    # cache.delete(f"file_format_{uuid}")
    # cache.delete(f"image_{uuid}")
    # cache.delete(f"image_information_{uuid}")
    if not image:
        raise Exception("Image not found.")

    return file_format, image, image_information
