from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

from .models import RegionStandard, CalculationRecord
from .serializers import (
    RegionStandardSerializer, CalculationRecordSerializer, SignupSerializer
)



class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


#추가
class SignupView(APIView):
    def post(self, request):
        s = SignupSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response({"detail": "회원가입 완료"}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    """
    액세스 토큰만 발급 (refresh는 미노출)
    """
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"detail": "아이디 또는 비밀번호가 올바르지 않습니다."},
                            status=status.HTTP_400_BAD_REQUEST)
        access = RefreshToken.for_user(user).access_token
        return Response({"access": str(access)})

class RegionStandardViewSet(viewsets.ReadOnlyModelViewSet):#유저용 분당단가 api
    queryset = RegionStandard.objects.all().order_by("region_code")
    serializer_class = RegionStandardSerializer

    # 간단한 필터 (region_code, education_office)
    def get_queryset(self):
        qs = super().get_queryset()
        rc = self.request.query_params.get("region_code")
        eo = self.request.query_params.get("education_office")
        if rc:
            qs = qs.filter(region_code__icontains=rc)
        if eo:
            qs = qs.filter(education_office__icontains=eo)
        return qs

class CalculationRecordViewSet(viewsets.ModelViewSet):
    serializer_class = CalculationRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CalculationRecord.objects.filter(user=self.request.user).order_by("-created_at")

class AdminRegionStandardViewSet(viewsets.ModelViewSet):#어드민 전용 분당단가 api
    queryset = RegionStandard.objects.all().order_by("region_code")
    serializer_class = RegionStandardSerializer
    permission_classes = [IsAdminUser]  # 관리자만 접근 가능
