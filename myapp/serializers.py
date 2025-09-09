from rest_framework import serializers
from .models import Book
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RegionStandard, CalculationRecord
from rest_framework.views import APIView
from .models import RegionStandard

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


#밑에는 내가 한거 

class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data.get("email") or "")
        user.set_password(validated_data["password"])
        user.save()
        return user

class RegionStandardSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionStandard
        fields = [
            "id",
            "region_code",
            "education_office",
            "subject_category",
            "standard_price",
            "effective_date",
            "source_url",
        ]

class CalculationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculationRecord
        read_only_fields = ("user", "total_minutes", "unit_price", "standard_price_at_calc", "is_valid", "created_at", "updated_at")
        fields = (
            "id", "user", "region_standard", "subject",
            "minutes_per_class", "months", "lessons_per_month", "tuition_fee",
            "total_minutes", "unit_price", "standard_price_at_calc", "is_valid",
            "created_at", "updated_at"
        )

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.recompute()
        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "date_joined")

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
