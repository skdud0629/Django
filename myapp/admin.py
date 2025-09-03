from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import RegionStandard

@admin.register(RegionStandard)
class RegionStandardAdmin(SimpleHistoryAdmin):
    list_display = (
        "region_code",
        "education_office",
        "subject_category",
        "standard_price",
        "tuition_fee",
        "lessons_per_week",
        "lessons_per_month",
        "minutes_per_class",
        "effective_date",
    )
    list_filter = ("education_office", "subject_category")
    search_fields = ("region_code", "education_office", "subject_category")
