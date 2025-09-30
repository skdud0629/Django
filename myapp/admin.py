
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import RegionStandard, CalculationRecord
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(RegionStandard)
class RegionStandardAdmin(SimpleHistoryAdmin):
    save_as = False
    save_on_top = False
    list_display = (
        "region_code",
        "education_office",
        "course_type",
        "standard_price",
        "effective_date",
    )
    list_filter = ("education_office", "course_type")
    search_fields = ("region_code", "education_office", "cursor_type")


# Inline 정의
class CalculationRecordInline(admin.TabularInline):
    model = CalculationRecord
    extra = 0
    fields = (
        "education_office",
        "subject",
        "minutes_per_class",
        "lessons_per_week",
        "lessons_per_month",
        "tuition_fee",
        "unit_price",
        "standard_price_at_calc",
        "is_valid",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("unit_price", "standard_price_at_calc", "created_at", "updated_at")


# 기존 UserAdmin 해제
admin.site.unregister(User)

# UserAdmin 확장 후 다시 등록
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_staff", "is_superuser", "last_login")
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_superuser")

    inlines = [CalculationRecordInline]
