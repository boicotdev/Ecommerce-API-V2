from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers.report_params import ReportParamsSerializer # serializers/report_params.py

from .serializers.report_params import ReportParamsSerializer
from .services.sales_report import SalesReportService
# from .services.stock_report import StockReportService

class SalesReportAPIView(APIView):
    def get(self, request):
            serializer = ReportParamsSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            data = serializer.validated_data

            service = SalesReportService(group_by=data["group_by"])
            result = service.generate(
                data["start_date"],
                data["end_date"]
            )

            return Response(result)
