# proj01/proj01/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.views import (
    RegionStandardViewSet,
    CalculationRecordViewSet,
    SignupView,
    LoginView,
)

router = DefaultRouter()
router.register(r"standards", RegionStandardViewSet, basename="standards")
router.register(r"calculations", CalculationRecordViewSet, basename="calculations")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/signup/", SignupView.as_view()),
    path("api/auth/login/", LoginView.as_view()),
    path("api/", include(router.urls)),
]
