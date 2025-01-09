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
        extracted_data = use_case.extract_text(image, document_type)  # type: ignore

        return Response({"data": extracted_data}, status=HTTP_200_OK)
    except Exception as error:
        return Response({"error": str(error)}, status=400)
