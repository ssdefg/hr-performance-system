from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.authentication.models import User
from apps.evaluations.models import EvaluationCriteria
from apps.evaluations.models import EvaluationItemScore, EvaluationReview
from apps.evaluations.serializers import (
    EvaluationCriteriaSerializer,
    EvaluationReviewSerializer,
    ReviewScoresInputSerializer,
)
from apps.evaluations.services import (
    calculate_final_score,
    calculate_grade,
    calculate_grade_roadmap,
    calculate_raw_score,
)
from apps.organizations.models import Team


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')


class EvaluationCriteriaViewSet(ModelViewSet):
    queryset = EvaluationCriteria.objects.all()
    serializer_class = EvaluationCriteriaSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'summary'):
            return [permissions.IsAuthenticated()]
        return [IsAdminRole()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role != 'ADMIN':
            queryset = queryset.filter(is_active=True)
        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        criteria = self.get_queryset().filter(is_active=True)
        total_weight = criteria.aggregate(total=Sum('weight'))['total'] or 0
        return Response({
            'criteria_count': criteria.count(),
            'total_weight': total_weight,
            'is_valid': total_weight == 100,
        })


def require_manager(user):
    if user.role != 'MANAGER':
        raise PermissionDenied('매니저만 평가 기능을 사용할 수 있습니다.')
    try:
        team = user.managed_teams
    except ObjectDoesNotExist:
        raise PermissionDenied('담당 팀이 지정되어 있지 않습니다.')
    return team


def get_team_employee(manager, employee_id):
    team = require_manager(manager)
    return get_object_or_404(User, employee_id=employee_id, team=team, role='EMPLOYEE')


def get_review_for_manager(manager, employee):
    return EvaluationReview.objects.filter(employee=employee, evaluator=manager).first()


def serialize_review(employee, manager, review=None):
    if review is None:
        return {
            'id': None,
            'employee_id': employee.employee_id,
            'employee_name': employee.name,
            'team_name': employee.team.name if employee.team_id else None,
            'status': 'NOT_STARTED',
            'scores': [],
            'raw_score': None,
            'final_score': None,
            'is_capped': False,
            'strengths': [],
            'improvements': [],
            'comment': '',
            'submitted_at': None,
            'updated_at': None,
        }
    return EvaluationReviewSerializer(review).data


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def team_members(request):
    team = require_manager(request.user)
    employees = User.objects.filter(team=team, role='EMPLOYEE').order_by('employee_id')
    reviews = {
        review.employee_id: review
        for review in EvaluationReview.objects.filter(evaluator=request.user, employee__in=employees)
    }
    members = []
    for employee in employees:
        review = reviews.get(employee.pk)
        members.append({
            'employee_id': employee.employee_id,
            'name': employee.name,
            'team_id': team.pk,
            'team_name': team.name,
            'review_status': review.status if review else 'NOT_STARTED',
            'raw_score': review.raw_score if review and review.status == 'SUBMITTED' else None,
        })
    submitted_count = sum(member['review_status'] == 'SUBMITTED' for member in members)
    return Response({
        'team_id': team.pk,
        'team_name': team.name,
        'member_count': len(members),
        'submitted_count': submitted_count,
        'members': members,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def manager_review(request, employee_id):
    employee = get_team_employee(request.user, employee_id)
    review = get_review_for_manager(request.user, employee)
    return Response(serialize_review(employee, request.user, review))


def save_review(request, employee_id, submit):
    employee = get_team_employee(request.user, employee_id)
    active_criteria = list(EvaluationCriteria.objects.filter(is_active=True).order_by('order', 'id'))
    total_weight = sum(criteria.weight for criteria in active_criteria)
    if total_weight != 100:
        raise ValidationError({'weight': '가중치 합계가 100이 아니므로 평가를 진행할 수 없습니다.'})

    serializer = ReviewScoresInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    score_data = serializer.validated_data['scores']
    score_map = {item['criteria_id']: item['score'] for item in score_data}
    active_ids = {criteria.id for criteria in active_criteria}
    if not set(score_map).issubset(active_ids):
        raise ValidationError({'scores': '활성 평가 항목만 입력할 수 있습니다.'})
    if submit and set(score_map) != active_ids:
        raise ValidationError({'scores': '최종 제출 전에 모든 평가 항목을 입력해야 합니다.'})

    with transaction.atomic():
        review = EvaluationReview.objects.select_for_update().filter(
            employee=employee,
            evaluator=request.user,
        ).first()
        if review is None:
            review = EvaluationReview(employee=employee, evaluator=request.user)

        review.status = 'SUBMITTED' if submit else (review.status or 'DRAFT')
        review.raw_score = calculate_raw_score(
            (score_map[criteria.id], criteria.weight)
            for criteria in active_criteria
            if criteria.id in score_map
        )
        team_bonus = employee.team.bonus_score if employee.team_id else 0
        review.final_score, review.is_capped = calculate_final_score(review.raw_score, team_bonus)
        
        # Save qualitative feedback
        if 'strengths' in serializer.validated_data:
            review.strengths = serializer.validated_data['strengths']
        if 'improvements' in serializer.validated_data:
            review.improvements = serializer.validated_data['improvements']
        if 'comment' in serializer.validated_data:
            review.comment = serializer.validated_data['comment']

        if submit:
            review.submitted_at = timezone.now()
        review.save()

        submitted_ids = set()
        for criteria in active_criteria:
            if criteria.id not in score_map:
                continue
            EvaluationItemScore.objects.update_or_create(
                review=review,
                criteria=criteria,
                defaults={'score': score_map[criteria.id]},
            )
            submitted_ids.add(criteria.id)
        review.scores.exclude(criteria_id__in=submitted_ids).delete()

    review = EvaluationReview.objects.prefetch_related('scores__criteria').select_related('employee__team').get(pk=review.pk)
    return Response(EvaluationReviewSerializer(review).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def save_draft(request, employee_id):
    return save_review(request, employee_id, submit=False)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_review(request, employee_id):
    return save_review(request, employee_id, submit=True)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_review(request):
    if request.user.role != 'EMPLOYEE':
        raise PermissionDenied('직원만 본인 평가를 조회할 수 있습니다.')
    review = EvaluationReview.objects.filter(
        employee=request.user,
        status='SUBMITTED',
    ).prefetch_related('scores__criteria').select_related('employee__team').first()
    if review is None:
        return Response({'status': 'IN_PROGRESS', 'message': '평가가 제출되면 결과를 확인할 수 있습니다.'})

    data = EvaluationReviewSerializer(review).data
    data['team_bonus'] = review.employee.team.bonus_score if review.employee.team_id else 0.0
    data['evaluator_name'] = review.evaluator.name
    data['grade'] = calculate_grade(review.final_score)
    data['roadmap'] = calculate_grade_roadmap(review.final_score)
    return Response(data)