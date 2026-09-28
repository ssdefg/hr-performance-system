import math

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from apps.evaluations.models import EvaluationReview
from apps.evaluations.services import calculate_final_score
from apps.organizations.models import Team
from apps.organizations.permissions import IsAdminRole
from apps.organizations.serializers import TeamSerializer


class TeamViewSet(ModelViewSet):
    queryset = Team.objects.select_related('manager').prefetch_related('members')
    serializer_class = TeamSerializer
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAdminRole()]

    @action(detail=True, methods=['post'])
    def bonus(self, request, pk=None):
        team = self.get_object()
        try:
            bonus_score = float(request.data['bonus_score'])
        except (KeyError, TypeError, ValueError):
            raise ValidationError({'bonus_score': '보너스 점수를 숫자로 입력해 주세요.'})
        if not math.isfinite(bonus_score) or not 0 <= bonus_score <= 10:
            raise ValidationError({'bonus_score': '보너스 점수는 0.0점에서 10.0점 사이여야 합니다.'})
        if round(bonus_score * 2) != bonus_score * 2:
            raise ValidationError({'bonus_score': '보너스 점수는 0.5점 단위로 입력해 주세요.'})

        with transaction.atomic():
            team.bonus_score = bonus_score
            team.save(update_fields=['bonus_score'])
            reviews = EvaluationReview.objects.select_for_update().filter(
                employee__team=team,
                status='SUBMITTED',
            )
            for review in reviews:
                review.final_score, review.is_capped = calculate_final_score(review.raw_score, bonus_score)
                review.save(update_fields=['final_score', 'is_capped', 'updated_at'])

        return Response({
            'team_id': team.pk,
            'team_name': team.name,
            'bonus_score': team.bonus_score,
            'updated_reviews': reviews.count(),
        }, status=status.HTTP_200_OK)