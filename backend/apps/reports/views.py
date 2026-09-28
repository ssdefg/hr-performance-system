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
from apps.evaluations.models import EvaluationCriteria, EvaluationItemScore, EvaluationReview
from apps.evaluations.scoring import calculate_grade
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
        final_score = review.final_score if submitted else None
        grade = calculate_grade(final_score) if submitted else None
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
            'final_score': final_score,
            'grade': grade,
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
    writer.writerow(['사번', '성명', '역할', '소속팀', '평가진행상태', '개인평가점수', '팀보너스', '최종점수', '등급', '상한적용여부'])
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
            row['grade'] or '',
            '예' if row['is_capped'] else '아니오',
        ])

    filename = f'HR_Performance_Review_{date.today():%Y%m%d}.csv'
    response = HttpResponse('\ufeff' + output.getvalue(), content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@api_view(['GET'])
@permission_classes([IsAdminRole])
def team_analytics(request):
    """
    팀별 역량 통계 및 등급별 상대평가 배분 현황 API
    """
    criteria_list = list(EvaluationCriteria.objects.filter(is_active=True).order_by('order', 'id'))
    criteria_labels = [c.name for c in criteria_list]
    criteria_ids = [c.id for c in criteria_list]

    teams = list(Team.objects.all().order_by('name'))
    submitted_reviews = list(EvaluationReview.objects.filter(status='SUBMITTED').select_related('employee__team'))

    item_scores_all = EvaluationItemScore.objects.filter(review__status='SUBMITTED')
    company_criteria_map = {}
    for cid in criteria_ids:
        scores = [item.score for item in item_scores_all if item.criteria_id == cid]
        avg = sum(scores) / len(scores) if scores else 0.0
        company_criteria_map[cid] = round(avg, 2)

    company_radar_data = [company_criteria_map.get(cid, 0.0) for cid in criteria_ids]

    teams_radar = []
    for team in teams:
        team_reviews = [r for r in submitted_reviews if r.employee.team_id == team.id]
        team_review_ids = [r.id for r in team_reviews]
        team_item_scores = [item for item in item_scores_all if item.review_id in team_review_ids]

        team_scores_list = []
        for cid in criteria_ids:
            scores = [item.score for item in team_item_scores if item.criteria_id == cid]
            avg = sum(scores) / len(scores) if scores else 0.0
            team_scores_list.append(round(avg, 2))

        teams_radar.append({
            'team_id': team.id,
            'team_name': team.name,
            'submitted_count': len(team_reviews),
            'bonus_score': team.bonus_score,
            'scores': team_scores_list,
        })

    target_distribution = {
        'S': 10.0,
        'A': 25.0,
        'B': 50.0,
        'C': 10.0,
        'D': 5.0,
    }

    grade_counts = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for r in submitted_reviews:
        g = calculate_grade(r.final_score)
        if g in grade_counts:
            grade_counts[g] += 1

    total_submitted = len(submitted_reviews)
    distribution_list = []
    summary_chips = []

    for grade in ['S', 'A', 'B', 'C', 'D']:
        count = grade_counts[grade]
        pct = round(count / total_submitted * 100, 1) if total_submitted > 0 else 0.0
        target_pct = target_distribution[grade]
        diff = round(pct - target_pct, 1)

        if total_submitted == 0:
            status_str = 'NORMAL'
            msg = f"{grade}등급 0.0% (권장 {int(target_pct)}%)"
        elif diff > 1.0:
            status_str = 'OVER'
            msg = f"{grade}등급 {pct}% (권장 {int(target_pct)}% 초과 +{diff}%p)"
        elif diff < -1.0:
            status_str = 'UNDER'
            msg = f"{grade}등급 {pct}% (권장 {int(target_pct)}% 미달 {diff}%p)"
        else:
            status_str = 'NORMAL'
            msg = f"{grade}등급 {pct}% (권장 {int(target_pct)}% 적정)"

        distribution_list.append({
            'grade': grade,
            'count': count,
            'percentage': pct,
            'recommended_percentage': target_pct,
            'diff_percentage': diff,
            'status': status_str,
            'message': msg,
        })
        summary_chips.append({
            'grade': grade,
            'status': status_str,
            'message': msg,
            'count': count,
            'percentage': pct,
            'recommended_percentage': target_pct,
        })

    cd_count = grade_counts['C'] + grade_counts['D']
    cd_pct = round(cd_count / total_submitted * 100, 1) if total_submitted > 0 else 0.0
    cd_diff = round(cd_pct - 15.0, 1)
    cd_status = 'OVER' if cd_diff > 1.0 else ('UNDER' if cd_diff < -1.0 else 'NORMAL')

    return Response({
        'criteria_labels': criteria_labels,
        'criteria_details': [{'id': c.id, 'name': c.name, 'weight': c.weight} for c in criteria_list],
        'company_radar': {
            'label': '전사 평균',
            'scores': company_radar_data,
        },
        'teams_radar': teams_radar,
        'distribution': {
            'total_submitted': total_submitted,
            'grades': distribution_list,
            'cd_combined': {
                'count': cd_count,
                'percentage': cd_pct,
                'recommended_percentage': 15.0,
                'diff_percentage': cd_diff,
                'status': cd_status,
            },
            'summary_chips': summary_chips,
        }
    })


@api_view(['GET'])
@permission_classes([IsAdminRole])
def admin_status(request):
    """
    관리자 메인 대시보드 및 응답 현황 모니터링 API
    """
    employees = list(User.objects.filter(role='EMPLOYEE', is_active=True).select_related('team').order_by('employee_id'))
    total_employees = len(employees)

    all_reviews = list(EvaluationReview.objects.all().select_related('evaluator', 'employee'))
    latest_reviews = {}
    for r in sorted(all_reviews, key=lambda x: (x.updated_at or x.created_at, x.id)):
        latest_reviews[r.employee_id] = r

    submitted_reviews = {eid: r for eid, r in latest_reviews.items() if r.status == 'SUBMITTED'}
    submitted_count = len(submitted_reviews)
    average = sum(r.final_score for r in submitted_reviews.values()) / submitted_count if submitted_count else 0.0

    teams = list(Team.objects.all().select_related('manager').order_by('name'))
    teams_with_bonus = sum(1 for t in teams if t.bonus_score > 0)

    kpi_data = {
        'total_employees': total_employees,
        'completion_rate': round(submitted_count / total_employees * 100, 1) if total_employees else 0.0,
        'completed_reviews': submitted_count,
        'company_average_score': round(average, 2),
        'bonus_summary': {
            'teams_with_bonus': teams_with_bonus,
            'total_teams': len(teams),
        },
    }

    teams_progress = []
    for team in teams:
        team_emps = [e for e in employees if e.team_id == team.id]
        t_total = len(team_emps)
        t_submitted = sum(1 for e in team_emps if latest_reviews.get(e.id) and latest_reviews[e.id].status == 'SUBMITTED')
        t_draft = sum(1 for e in team_emps if latest_reviews.get(e.id) and latest_reviews[e.id].status == 'DRAFT')
        t_not_started = t_total - t_submitted - t_draft
        t_rate = round(t_submitted / t_total * 100, 1) if t_total else 0.0

        status_val = 'COMPLETED' if (t_total > 0 and t_submitted == t_total) else ('IN_PROGRESS' if (t_submitted > 0 or t_draft > 0) else 'NOT_STARTED')

        teams_progress.append({
            'team_id': team.id,
            'team_name': team.name,
            'manager_name': team.manager.name if team.manager else '미지정',
            'manager_employee_id': team.manager.employee_id if team.manager else None,
            'total_members': t_total,
            'submitted_count': t_submitted,
            'draft_count': t_draft,
            'not_started_count': t_not_started,
            'completion_rate': t_rate,
            'status': status_val,
        })

    managers = list(User.objects.filter(role='MANAGER', is_active=True).select_related('team').order_by('name'))
    manager_status = []
    for mgr in managers:
        managed_team = next((t for t in teams if t.manager_id == mgr.id), None)
        if managed_team:
            mgr_emps = [e for e in employees if e.team_id == managed_team.id]
            tname = managed_team.name
        elif mgr.team_id:
            mgr_emps = [e for e in employees if e.team_id == mgr.team_id]
            tname = mgr.team.name
        else:
            mgr_emps = []
            tname = '미배정'

        m_total = len(mgr_emps)
        m_submitted = sum(1 for e in mgr_emps if latest_reviews.get(e.id) and latest_reviews[e.id].status == 'SUBMITTED')
        m_draft = sum(1 for e in mgr_emps if latest_reviews.get(e.id) and latest_reviews[e.id].status == 'DRAFT')
        m_pending = m_total - m_submitted
        m_rate = round(m_submitted / m_total * 100, 1) if m_total else 0.0

        unsub_list = []
        for e in mgr_emps:
            rev = latest_reviews.get(e.id)
            if not rev or rev.status != 'SUBMITTED':
                unsub_list.append({
                    'employee_id': e.employee_id,
                    'name': e.name,
                    'status': rev.status if rev else 'NOT_STARTED',
                })

        status_val = 'COMPLETED' if (m_total > 0 and m_submitted == m_total) else ('IN_PROGRESS' if (m_submitted > 0 or m_draft > 0) else 'NOT_STARTED')

        manager_status.append({
            'manager_id': mgr.id,
            'employee_id': mgr.employee_id,
            'name': mgr.name,
            'team_name': tname,
            'total_members': m_total,
            'submitted_count': m_submitted,
            'draft_count': m_draft,
            'pending_count': m_pending,
            'completion_rate': m_rate,
            'status': status_val,
            'unsubmitted_members': unsub_list,
        })

    return Response({
        'kpi': kpi_data,
        'teams_progress': teams_progress,
        'manager_status': manager_status,
    })


@api_view(['GET'])
@permission_classes([IsAdminRole])
def dashboard_stats(request):
    """
    관리자 대시보드 통합 통계 API:
    1. KPI 요약
    2. 팀별 평균 점수 (Bar Chart)
    3. 팀별 등급 분포 (Grouped/Stacked Bar Chart)
    4. 평가 항목별 팀 평균 점수 (Radar Chart)
    5. 개인별 점수 목록 (Table)
    """
    employees = list(User.objects.filter(role='EMPLOYEE', is_active=True).select_related('team').order_by('employee_id'))
    total_employees = len(employees)

    all_reviews = list(EvaluationReview.objects.all().select_related('evaluator', 'employee'))
    latest_reviews = {}
    for r in sorted(all_reviews, key=lambda x: (x.updated_at or x.created_at, x.id)):
        latest_reviews[r.employee_id] = r

    submitted_reviews = {eid: r for eid, r in latest_reviews.items() if r.status == 'SUBMITTED'}
    submitted_count = len(submitted_reviews)
    overall_average = round(sum(r.final_score for r in submitted_reviews.values()) / submitted_count, 2) if submitted_count else 0.0
    submission_rate = round(submitted_count / total_employees * 100, 1) if total_employees else 0.0

    teams = list(Team.objects.all().order_by('name'))
    teams_with_bonus = sum(1 for t in teams if t.bonus_score > 0)

    # 1. KPI Summary
    kpi_summary = {
        'total_employees': total_employees,
        'submission_rate': submission_rate,
        'completed_reviews': submitted_count,
        'overall_average': overall_average,
        'bonus_applied_teams': f"{teams_with_bonus} / {len(teams)}팀",
        'bonus_summary': {
            'teams_with_bonus': teams_with_bonus,
            'total_teams': len(teams),
        },
    }

    # 2. Team Averages (Bar Chart)
    team_names = [t.name for t in teams]
    team_averages_data = []
    for t in teams:
        t_sub_reviews = [r for eid, r in submitted_reviews.items() if r.employee.team_id == t.id]
        if t_sub_reviews:
            avg = round(sum(r.final_score for r in t_sub_reviews) / len(t_sub_reviews), 2)
        else:
            avg = 0.0
        team_averages_data.append(avg)

    team_averages = {
        'labels': team_names,
        'data': team_averages_data,
    }

    # 3. Team Grade Distribution (Doughnut & Bar Details)
    grade_colors = {
        'S': {'bg': '#7048e8', 'border': '#5f3dc4'},
        'A': {'bg': '#206bc4', 'border': '#185499'},
        'B': {'bg': '#2fb344', 'border': '#248c35'},
        'C': {'bg': '#f59f00', 'border': '#cc8500'},
        'D': {'bg': '#d63939', 'border': '#ae2e2e'},
    }

    team_grade_counts = {t.id: {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0} for t in teams}
    team_grade_employees = {t.id: {'S': [], 'A': [], 'B': [], 'C': [], 'D': []} for t in teams}
    company_grade_employees = {'S': [], 'A': [], 'B': [], 'C': [], 'D': []}

    for eid, r in submitted_reviews.items():
        tid = r.employee.team_id
        g = calculate_grade(r.final_score)
        emp_info = {
            'employee_id': r.employee.employee_id,
            'name': r.employee.name,
            'team_name': r.employee.team.name if r.employee.team else '',
            'score': r.final_score,
        }
        if g in company_grade_employees:
            company_grade_employees[g].append(emp_info)
        if tid in team_grade_counts and g in team_grade_counts[tid]:
            team_grade_counts[tid][g] += 1
            team_grade_employees[tid][g].append(emp_info)

    distribution_datasets = []
    for g in ['S', 'A', 'B', 'C', 'D']:
        distribution_datasets.append({
            'label': f'{g}등급',
            'grade': g,
            'data': [team_grade_counts[t.id][g] for t in teams],
            'backgroundColor': grade_colors[g]['bg'],
            'borderColor': grade_colors[g]['border'],
            'borderWidth': 1,
        })

    teams_detail = []
    for t in teams:
        t_emps = [e for e in employees if e.team_id == t.id]
        t_sub_count = sum(team_grade_counts[t.id].values())
        teams_detail.append({
            'team_id': t.id,
            'team_name': t.name,
            'total_members': len(t_emps),
            'submitted_count': t_sub_count,
            'grades': {
                g: {
                    'count': team_grade_counts[t.id][g],
                    'names': [e['name'] for e in team_grade_employees[t.id][g]],
                    'employees': team_grade_employees[t.id][g],
                }
                for g in ['S', 'A', 'B', 'C', 'D']
            },
        })

    team_grade_distribution = {
        'labels': team_names,
        'grades': ['S', 'A', 'B', 'C', 'D'],
        'datasets': distribution_datasets,
        'teams_detail': teams_detail,
        'company_detail': {
            'total_submitted': len(submitted_reviews),
            'total_members': len(employees),
            'grades': {
                g: {
                    'count': len(company_grade_employees[g]),
                    'names': [e['name'] for e in company_grade_employees[g]],
                    'employees': company_grade_employees[g],
                }
                for g in ['S', 'A', 'B', 'C', 'D']
            },
        },
    }

    # 4. Criteria Team Radar (Spider Chart)
    criteria_list = list(EvaluationCriteria.objects.filter(is_active=True).order_by('order', 'id'))
    criteria_labels = [c.name for c in criteria_list]
    criteria_ids = [c.id for c in criteria_list]

    item_scores_all = list(EvaluationItemScore.objects.filter(review__status='SUBMITTED'))

    company_radar_scores = []
    for cid in criteria_ids:
        scores = [item.score for item in item_scores_all if item.criteria_id == cid]
        avg = round(sum(scores) / len(scores), 2) if scores else 0.0
        company_radar_scores.append(avg)

    radar_palette = [
        {'bg': 'rgba(32, 107, 196, 0.25)', 'border': '#206bc4'},
        {'bg': 'rgba(47, 179, 68, 0.25)', 'border': '#2fb344'},
        {'bg': 'rgba(245, 159, 0, 0.25)', 'border': '#f59f00'},
        {'bg': 'rgba(112, 72, 232, 0.25)', 'border': '#7048e8'},
    ]

    team_radar_datasets = [
        {
            'label': '전사 평균',
            'data': company_radar_scores,
            'backgroundColor': 'rgba(148, 163, 184, 0.15)',
            'borderColor': '#94a3b8',
            'borderWidth': 2,
            'borderDash': [4, 4],
            'pointBackgroundColor': '#94a3b8',
        }
    ]

    for idx, t in enumerate(teams):
        palette = radar_palette[idx % len(radar_palette)]
        t_rev_ids = [r.id for eid, r in submitted_reviews.items() if r.employee.team_id == t.id]
        t_item_scores = [item for item in item_scores_all if item.review_id in t_rev_ids]
        t_scores = []
        for cid in criteria_ids:
            scores = [item.score for item in t_item_scores if item.criteria_id == cid]
            avg = round(sum(scores) / len(scores), 2) if scores else 0.0
            t_scores.append(avg)

        team_radar_datasets.append({
            'label': t.name,
            'data': t_scores,
            'backgroundColor': palette['bg'],
            'borderColor': palette['border'],
            'borderWidth': 2,
            'pointBackgroundColor': palette['border'],
        })

    criteria_team_radar = {
        'labels': criteria_labels,
        'datasets': team_radar_datasets,
    }

    # 5. Individual Scores Table
    table_rows = []
    for emp in employees:
        rev = latest_reviews.get(emp.id)
        is_sub = rev is not None and rev.status == 'SUBMITTED'
        final_sc = rev.final_score if is_sub else None
        gr = calculate_grade(final_sc) if is_sub else None
        table_rows.append({
            'id': emp.id,
            'employee_id': emp.employee_id,
            'name': emp.name,
            'team_name': emp.team.name if emp.team else '미배정',
            'raw_score': rev.raw_score if is_sub else None,
            'bonus_score': emp.team.bonus_score if emp.team else 0.0,
            'final_score': final_sc,
            'grade': gr,
            'review_status': rev.status if rev else 'NOT_STARTED',
            'is_capped': rev.is_capped if is_sub else False,
        })

    return Response({
        'kpi': kpi_summary,
        'team_averages': team_averages,
        'team_grade_distribution': team_grade_distribution,
        'criteria_team_radar': criteria_team_radar,
        'score_table': table_rows,
    })