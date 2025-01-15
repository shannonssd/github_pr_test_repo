from uuid import UUID

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from extractify_api.use_cases import gpt as use_case


@api_view(["POST"])
def extract_text(request: Request) -> Response:
    """"""
    try:
        print("HTTP request received")
        data = request.data
        image = data.get("image")
        document_type = data.get("document_type")
        uuid = use_case.extract_text(image, document_type)  # type: ignore

        return Response({"uuid": uuid}, status=HTTP_200_OK)
    except Exception as error:
        return Response({"error": str(error)}, status=400)


@api_view(["GET"])
def retrieve_data(request: Request, uuid: UUID) -> Response:
    """"""
    try:
        print("HTTP request received")
        print("UUID:", uuid)
        file_format, image, image_information = use_case.retrieve_data(uuid)  # type: ignore

        return Response(
            {"file_format": file_format, "image": image, "image_information": image_information},
            status=HTTP_200_OK,
        )
    except Exception as error:
        return Response({"error": str(error)}, status=400)
