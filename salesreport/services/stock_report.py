from django.db.models import Sum
from .base import BaseReportService
# from inventory.models import StockMovement
#
# class StockReportService(BaseReportService):
#
#     def get_queryset(self, start_date, end_date):
#         return StockMovement.objects.filter(
#             created_at__date__range=(start_date, end_date)
#         )
#
#     def generate(self, start_date, end_date):
#         qs = self.get_queryset(start_date, end_date)
#         qs = self.apply_grouping()
#
#         return (
#             qs.values("period")
#               .annotate(
#                   total_in=Sum("quantity", filter=Q(type="IN")),
#                   total_out=Sum("quantity", filter=Q(type="OUT"))
#               )
#               .order_by("period")
#         )
