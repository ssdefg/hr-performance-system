from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator

class EvaluationCriteria(models.Model):
    name = models.CharField(max_length=150, verbose_name='평가 항목명')
    description = models.TextField(blank=True, verbose_name='항목 설명')
    weight = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name='가중치(%)',
    )
    order = models.PositiveIntegerField(default=1, verbose_name='정렬 순서')
    is_active = models.BooleanField(default=True, verbose_name='활성화 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        verbose_name = '평가 기준 항목'
        verbose_name_plural = '평가 기준 항목 목록'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.name} (가중치: {self.weight}%)"

class EvaluationReview(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', '임시 저장'),
        ('SUBMITTED', '제출 완료'),
    )

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        verbose_name='피평가자(직원)'
    )
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conducted_reviews',
        verbose_name='평가자(매니저)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name='평가 상태')
    raw_score = models.FloatField(default=0.0, verbose_name='개인 평가 점수')
    final_score = models.FloatField(default=0.0, verbose_name='최종 산출 점수')
    is_capped = models.BooleanField(default=False, verbose_name='100점 상한 적용 여부')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='최종 제출일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        verbose_name = '인사 평가서'
        verbose_name_plural = '인사 평가서 목록'
        unique_together = ('employee', 'evaluator')

    def __str__(self):
        return f"[{self.get_status_display()}] {self.employee.name} (평가자: {self.evaluator.name}) - 최종 {self.final_score}점"

class EvaluationItemScore(models.Model):
    review = models.ForeignKey(
        EvaluationReview,
        on_delete=models.CASCADE,
        related_name='scores',
        verbose_name='평가서'
    )
    criteria = models.ForeignKey(
        EvaluationCriteria,
        on_delete=models.CASCADE,
        related_name='item_scores',
        verbose_name='평가 항목'
    )
    score = models.PositiveSmallIntegerField(verbose_name='부여 점수(1~5점)')

    class Meta:
        verbose_name = '항목별 평가 점수'
        verbose_name_plural = '항목별 평가 점수 목록'
        unique_together = ('review', 'criteria')

    def __str__(self):
        return f"{self.criteria.name}: {self.score}점"
