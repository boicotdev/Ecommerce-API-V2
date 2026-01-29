from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from salesreport.serializers.serializers import SalesDataReportSerializer
from .serializers.report_params import ReportParamsSerializer
from .services.sales_report import SalesReportService
from .services.stock_report import StockReportService
from users.models import User
from payments.models import Payment

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
        result = None
        data = serializer.validated_data

        #TODO: Save the report data inside of database.
        if report_type == 'sales':
            service = SalesReportService(group_by=data['group_by'])
            report = BaseReportHandler(serializer, service)
            result = report.result
            return Response(result, status = status.HTTP_200_OK)
        else:
            service = StockReportService(group_by=data['group_by'])
            report = BaseReportHandler(serializer, service)
            result = report.result
            return Response(result, status = status.HTTP_200_OK)

class AnalyticsSalesReportsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        months = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}
        sales_data = []
        for i, month in enumerate(months):
            # i = i + 1
            sales_data.append({
                'month': month,
                'revenue': sum([item.payment_amount for item in Payment.objects.filter(payment_date__month=i)]),
                'orders': Payment.objects.filter(payment_date__month=i).count(),
                'customers': User.objects.filter(date_joined__month=i).count()
            })

            
        serializer = SalesDataReportSerializer(data=sales_data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response({
            'sales_data': serializer.data,
        }, status = status.HTTP_200_OK)




