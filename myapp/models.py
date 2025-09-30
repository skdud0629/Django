from django.db import models
from django.contrib.auth.models import User

from django.conf import settings
from decimal import Decimal, ROUND_DOWN

from simple_history.models import HistoricalRecords


class Meta:#중복 저장 예외
    constraints = [
        models.UniqueConstraint(
            fields=["region_code", "course_type", "subject_category", "effective_date"],
            name="unique_region_course_subject_date"
        )
    ]

# Create your models here. 테스트 
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    published_date = models.DateField()

'''
class RegionStandard(models.Model):
    region_code = models.CharField(max_length=100)  # 예: "서울_성북"
    education_office = models.CharField(max_length=255)  # 예: "서울특별시성북강북교육지원청"
    course_type = models.CharField(max_length=50)  # 예: "개인", "그룹"
    subject_category = models.CharField(max_length=50)  # 예: "미술", "음악"
    standard_price = models.FloatField()  # 기준 분당 단가
    effective_date = models.DateField($)  # 기준 단가 적용일

    def __str__(self):
        return f"{self.region_code} - {self.course_type} - {self.subject_category}"
'''

#이 아래는 내가 추가한 거

class RegionStandard(models.Model):
    region_code = models.CharField(max_length=100)         # 예: "서울_성북"
    education_office = models.CharField(max_length=100)    # 예: "서울 성북교육지원청"
    course_type = models.CharField(max_length=50)     # 예: 보습-초등    
    # 기준 단가 (양의 정수, 분당 단가)
    standard_price = models.PositiveIntegerField()  

    # 적용일 (자동 변경)
    effective_date = models.DateField(auto_now=True)
    
    # 출처 URL
    source_url = models.URLField(null=True, blank=True)

    # 변경 이력 추적
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.region_code}"

class CalculationRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="calculations")
    education_office =models.CharField(max_length=100)

    course_type=models.CharField(max_length=100, default="교습과정구분 정보를 입력해주세요.")
    subject = models.CharField(max_length=100, )  # 예: "피아노"
    minutes_per_class = models.PositiveIntegerField()
    lessons_per_week = models.PositiveIntegerField(null=True)
    lessons_per_month = models.FloatField()
    tuition_fee = models.PositiveIntegerField(help_text="총 교습비(원)")

    # 파생값
    total_minutes = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)          # 분당 단가 (소수 둘째 자리 내림)
    standard_price_at_calc = models.DecimalField(max_digits=10, decimal_places=2)
    is_valid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def _floor_2(value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_DOWN)
    def recompute(self):
        # total_minutes만 서버에서 계산
        total = self.minutes_per_class * self.lessons_per_month
        if total <= 0:
            raise ValueError("총 수업 시간은 1분 이상이어야 합니다.")
        self.total_minutes = total

        # unit_price, standard_price_at_calc는 클라에서 온 값이 있으면 덮어쓰지 않음
        if not self.unit_price:  # DB에 값이 없을 때만 계산
            unit = Decimal(self.tuition_fee) / Decimal(total)
            self.unit_price = self._floor_2(unit)

        if not self.standard_price_at_calc:  # 클라가 준 값이 없을 때만 RegionStandard 참고
            try:
                region_instance = RegionStandard.objects.get(region_code=self.education_office)
                self.standard_price_at_calc = Decimal(region_instance.standard_price)
                self.is_valid = self.unit_price <= self.standard_price_at_calc
            except RegionStandard.DoesNotExist:
                self.standard_price_at_calc = Decimal("0.00")
                self.is_valid = False


            
    def save(self, *args, **kwargs):
        # 파생 필드 자동 계산
        self.recompute()
        super().save(*args, **kwargs)
