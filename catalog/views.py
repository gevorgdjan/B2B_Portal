from celery.result import AsyncResult
from django.core.files.storage import default_storage
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ProductFilter
from .models import Product
from .serializers import PriceListUploadSerializer, ProductSerializer
from .tasks import process_price_list_task


class ImportPriceListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @extend_schema(
        operation_id="upload_price_list",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary",
                    }
                },
                "required": ["file"],
            }
        },
        responses={202: None},
    )
    def post(self, request):
        serializer = PriceListUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data["file"]

        file_path = default_storage.save(f"tmp/{file_obj.name}", file_obj)
        task = process_price_list_task.delay(file_path)

        return Response(
            {"message": "Прайс-лист добавлен в очередь на обработку", "task_id": task.id},
            status=status.HTTP_202_ACCEPTED,
        )

class TaskStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: dict}, operation_id="check_task_status")
    def get(self, request, task_id: str):
        task_result = AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ProductListAPIView(ListAPIView):
    permission_classes = [AllowAny]

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter