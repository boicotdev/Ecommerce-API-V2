from datetime import datetime, time
from django.utils.timezone import make_aware
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from orders.models import OrderProduct

class StockReportService:

    def __init__(self, group_by):
        self.group_by = group_by

    def generate(self, start_date, end_date):
        start_dt = make_aware(datetime.combine(start_date, time.min))
        end_dt = make_aware(datetime.combine(end_date, time.max))

        qs = OrderProduct.objects.filter(
            order__created_at__gte=start_dt,
            order__created_at__lte=end_dt,
        ).exclude(
            order__status__in=["CANCELLED", "FAILED"]
        )

        if self.group_by == "day":
            qs = qs.annotate(period=TruncDay("order__created_at"))
        elif self.group_by == "month":
            qs = qs.annotate(period=TruncMonth("order__created_at"))
        elif self.group_by == "year":
            qs = qs.annotate(period=TruncYear("order__created_at"))

        return (
            qs.values("period", "product_id", "product__name")
              .annotate(
                  total_out=Sum("quantity"),
                  orders_count=Count("order", distinct=True),
              )
              .order_by("period")
        )
