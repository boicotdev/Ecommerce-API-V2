from datetime import datetime
from django.db.models import Value, Sum, Count
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from payments.models import Payment

class SalesReportService:

    def __init__(self, group_by):
        self.group_by = group_by

    def _apply_grouping(self, queryset):
        if self.group_by == "day":
            return queryset.annotate(period=TruncDay("payment_date"))
        if self.group_by == "month":
            return queryset.annotate(period=TruncMonth("payment_date"))
        if self.group_by == "year":
            return queryset.annotate(period=TruncYear("payment_date"))

    def generate(self, start_date, end_date):
        qs = Payment.objects.filter(
            payment_status="APPROVED",
            payment_date__date__range=(start_date, end_date)
        )

        qs = self._apply_grouping(qs)

        return (
            qs.values("period")
              .annotate(
                  total_sales=Sum("payment_amount"),
                  net_sales=Sum("net_received_amount"),
                  taxes=Sum("taxes_amount"),
                  total_transactions=Count("id"),
                  created_at=Value(str(datetime.now())),
              )
              .order_by("period")
        )
