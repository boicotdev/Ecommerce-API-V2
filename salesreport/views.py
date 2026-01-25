from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers.report_params import ReportParamsSerializer # serializers/report_params.py
from rest_framework.permissions import IsAdminUser
from .serializers.report_params import ReportParamsSerializer
from .services.sales_report import SalesReportService
from .services.stock_report import StockReportService


class BaseReportHandler:
    def __init__(self,serializer, service) -> None:
        self.serializer = serializer
        self.service = service
        self.__data = self.serializer.validated_data
        self.result = self.service.generate(
            self.__data['start_date'],
            self.__data['end_date'],
        )

class ReportsAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        report_type = request.query_params.get('type')
        serializer = ReportParamsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if report_type == 'sales':
            service = SalesReportService(group_by=data['group_by'])
            report = BaseReportHandler(serializer, service)
            return Response(report.result, status = status.HTTP_200_OK)
        else:
            service = StockReportService(group_by=data['group_by'])
            report = BaseReportHandler(serializer, service)
            return Response(report.result, status = status.HTTP_200_OK)

