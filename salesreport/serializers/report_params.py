from rest_framework import serializers


class ReportParamsSerializer(serializers.Serializer):
    REPORT_TYPES = (
        ("sales", "Sales"),
        ("stock", "Stock"),
    )

    GROUP_BY = (
        ("day", "Day"),
        ("month", "Month"),
        ("year", "Year"),
    )

    type = serializers.ChoiceField(choices=REPORT_TYPES)
    group_by = serializers.ChoiceField(choices=GROUP_BY)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
