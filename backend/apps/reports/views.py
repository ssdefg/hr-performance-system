import csv
from datetime import date
from io import StringIO

from django.db.models import Avg, Count
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from apps.authentication.models import User
from apps.evaluations.models import EvaluationReview
from apps.organizations.models import Team


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')


def selected_team(request):
    team_id = request.query_params.get('team_id')
    if not team_id:
        return None
    try:
        return Team.objects.get(pk=team_id)
    except (Team.DoesNotExist, ValueError):
        raise ValidationError({'team_id': '유효한 팀을 선택해 주세요.'})


def submitted_reviews_by_employee(employees):
    reviews = EvaluationReview.objects.filter(
        employee__in=employees,
        status='SUBMITTED',
    ).select_related('evaluator').order_by('employee_id', '-submitted_at', '-id')
    latest = {}
    for review in reviews:
        latest.setdefault(review.employee_id, review)
    return latest


def score_rows(request):
    team = selected_team(request)
    employees = User.objects.filter(role='EMPLOYEE').select_related('team').order_by('employee_id')
    if team:
        employees = employees.filter(team=team)
    latest_reviews = {}
    reviews = EvaluationReview.objects.filter(
        employee__in=employees,
    ).select_related('evaluator').order_by('employee_id', '-updated_at', '-id')
    for review in reviews:
        latest_reviews.setdefault(review.employee_id, review)
    rows = []
    for employee in employees:
        review = latest_reviews.get(employee.pk)
        submitted = review is not None and review.status == 'SUBMITTED'
        rows.append({
            'id': employee.pk,
            'employee_id': employee.employee_id,
            'name': employee.name,
            'role': employee.role,
            'team_id': employee.team_id,
            'team_name': employee.team.name if employee.team_id else None,
            'manager_name': review.evaluator.name if review else (employee.team.manager.name if employee.team_id and employee.team.manager_id else None),
            'review_status': review.status if review else 'NOT_STARTED',
            'raw_score': review.raw_score if submitted else None,
            'bonus_score': employee.team.bonus_score if employee.team_id else 0.0,
            'final_score': review.final_score if submitted else None,
            'is_capped': review.is_capped if submitted else False,
        })
    return rows


@api_view(['GET'])
@permission_classes([IsAdminRole])
def dashboard_kpi(request):
    employees = User.objects.filter(role='EMPLOYEE', is_active=True)
    total_employees = employees.count()
    reviews = submitted_reviews_by_employee(employees)
    submitted_count = len(reviews)
    average = sum(review.final_score for review in reviews.values()) / submitted_count if submitted_count else 0
    teams_total = Team.objects.count()
    teams_with_bonus = Team.objects.filter(bonus_score__gt=0).count()
    return Response({
        'total_employees': total_employees,
        'completion_rate': round(submitted_count / total_employees * 100, 1) if total_employees else 0.0,
        'completed_reviews': submitted_count,
        'company_average_score': round(average, 2),
        'bonus_summary': {
            'teams_with_bonus': teams_with_bonus,
            'total_teams': teams_total,
        },
    })


@api_view(['GET'])
@permission_classes([IsAdminRole])
def score_table(request):
    return Response(score_rows(request))


@api_view(['GET'])
@permission_classes([IsAdminRole])
def export_csv(request):
    output = StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(['사번', '성명', '역할', '소속팀', '평가진행상태', '개인평가점수', '팀보너스', '최종점수', '상한적용여부'])
    for row in score_rows(request):
        writer.writerow([
            row['employee_id'],
            row['name'],
            row['role'],
            row['team_name'] or '',
            row['review_status'],
            '' if row['raw_score'] is None else f"{row['raw_score']:.2f}",
            f"{row['bonus_score']:.1f}",
            '' if row['final_score'] is None else f"{row['final_score']:.2f}",
            '예' if row['is_capped'] else '아니오',
        ])

    filename = f'HR_Performance_Review_{date.today():%Y%m%d}.csv'
    response = HttpResponse('\ufeff' + output.getvalue(), content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response