from django.db import models
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='팀명')
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'MANAGER'},
        related_name='managed_teams',
        verbose_name='담당 매니저'
    )
    bonus_score = models.FloatField(default=0.0, verbose_name='팀 보너스 점수')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        verbose_name = '팀'
        verbose_name_plural = '팀 목록'
        ordering = ['name']

    def __str__(self):
        manager_name = self.manager.name if self.manager else '매니저 미지정'
        return f"{self.name} (매니저: {manager_name}, 보너스: +{self.bonus_score}점)"
