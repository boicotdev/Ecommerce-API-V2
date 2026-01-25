from django.db.models.functions import TruncDay, TruncMonth, TruncYear

class BaseReportService:

    def __init__(self, queryset, group_by):
        self.queryset = queryset
        self.group_by = group_by

    def _apply_grouping(self):
        if self.group_by == "day":
            return self.queryset.annotate(period=TruncDay("created_at"))
        if self.group_by == "month":
            return self.queryset.annotate(period=TruncMonth("created_at"))
        if self.group_by == "year":
            return self.queryset.annotate(period=TruncYear("created_at"))
