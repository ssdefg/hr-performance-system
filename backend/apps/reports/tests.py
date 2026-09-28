import codecs
import csv
from io import StringIO

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.evaluations.models import EvaluationCriteria, EvaluationItemScore, EvaluationReview
from apps.evaluations.scoring import calculate_grade
from apps.organizations.models import Team


class ReportingAndBonusApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.get(employee_id='ADMIN')
        self.manager = user_model.objects.create_user(
            employee_id='MGR-RPT', name='담당 매니저', password='pass1234', role='MANAGER'
        )
        self.team = Team.objects.create(name='보고팀', manager=self.manager, bonus_score=0)
        self.manager.team = self.team
        self.manager.save(update_fields=['team'])
        self.employee = user_model.objects.create_user(
            employee_id='EMP-RPT', name='홍길동', password='pass1234', role='EMPLOYEE', team=self.team
        )
        self.criteria = EvaluationCriteria.objects.create(name='성과', weight=100, order=1)
        self.review = EvaluationReview.objects.create(
            employee=self.employee,
            evaluator=self.manager,
            status='SUBMITTED',
            raw_score=82,
            final_score=82,
        )
        EvaluationItemScore.objects.create(review=self.review, criteria=self.criteria, score=4)
        self.client.force_authenticate(self.admin)

    def test_grade_calculation_function(self):
        self.assertEqual(calculate_grade(95.0), 'S')
        self.assertEqual(calculate_grade(98.5), 'S')
        self.assertEqual(calculate_grade(94.9), 'A')
        self.assertEqual(calculate_grade(90.0), 'A')
        self.assertEqual(calculate_grade(89.9), 'B')
        self.assertEqual(calculate_grade(80.0), 'B')
        self.assertEqual(calculate_grade(79.9), 'C')
        self.assertEqual(calculate_grade(70.0), 'C')
        self.assertEqual(calculate_grade(69.9), 'D')
        self.assertEqual(calculate_grade(0.0), 'D')
        self.assertIsNone(calculate_grade(None))

    def test_team_bonus_recalculates_submitted_reviews(self):
        response = self.client.post(f'/api/teams/{self.team.pk}/bonus/', {'bonus_score': 5}, format='json')
        self.review.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['updated_reviews'], 1)
        self.assertEqual(self.review.final_score, 87)
        self.assertFalse(self.review.is_capped)

    def test_team_bonus_caps_scores_and_sets_flag(self):
        self.review.raw_score = 98
        self.review.save(update_fields=['raw_score'])

        response = self.client.post(f'/api/teams/{self.team.pk}/bonus/', {'bonus_score': 5}, format='json')
        self.review.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.review.final_score, 100)
        self.assertTrue(self.review.is_capped)

    def test_invalid_bonus_is_rejected(self):
        response = self.client.post(f'/api/teams/{self.team.pk}/bonus/', {'bonus_score': 10.5}, format='json')

        self.assertEqual(response.status_code, 400)

    def test_non_finite_bonus_is_rejected(self):
        response = self.client.post(
            f'/api/teams/{self.team.pk}/bonus/',
            data='{"bonus_score": Infinity}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)

    def test_dashboard_kpi_and_team_filtered_score_table(self):
        self.client.post(f'/api/teams/{self.team.pk}/bonus/', {'bonus_score': 5}, format='json')

        kpi = self.client.get('/api/reports/dashboard-kpi/')
        table = self.client.get(f'/api/reports/score-table/?team_id={self.team.pk}')

        self.assertEqual(kpi.status_code, 200)
        self.assertEqual(kpi.data['total_employees'], 1)
        self.assertEqual(kpi.data['completion_rate'], 100.0)
        self.assertEqual(kpi.data['company_average_score'], 87.0)
        self.assertEqual(len(table.data), 1)
        self.assertEqual(table.data[0]['final_score'], 87)
        self.assertEqual(table.data[0]['grade'], 'B')

    def test_score_table_preserves_draft_status_without_publishing_scores(self):
        draft_employee = get_user_model().objects.create_user(
            employee_id='EMP-DRAFT', name='임시 저장 직원', password='pass1234', role='EMPLOYEE', team=self.team
        )
        EvaluationReview.objects.create(
            employee=draft_employee,
            evaluator=self.manager,
            status='DRAFT',
            raw_score=40,
            final_score=40,
        )

        response = self.client.get(f'/api/reports/score-table/?team_id={self.team.pk}')
        draft_row = next(row for row in response.data if row['employee_id'] == 'EMP-DRAFT')

        self.assertEqual(draft_row['review_status'], 'DRAFT')
        self.assertIsNone(draft_row['raw_score'])
        self.assertIsNone(draft_row['final_score'])
        self.assertIsNone(draft_row['grade'])

    def test_csv_has_utf8_bom_and_korean_headers(self):
        response = self.client.get('/api/reports/export-csv/')
        content = response.content

        self.assertEqual(response.status_code, 200)
        self.assertTrue(content.startswith(codecs.BOM_UTF8))
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('filename="HR_Performance_Review_', response['Content-Disposition'])
        rows = list(csv.reader(StringIO(content.decode('utf-8-sig').lstrip('\ufeff'))))
        self.assertEqual(rows[0][0:5], ['사번', '성명', '역할', '소속팀', '평가진행상태'])
        self.assertIn('등급', rows[0])
        self.assertEqual(rows[1][0], 'EMP-RPT')
        self.assertEqual(rows[1][8], 'B')  # 82점 -> B등급

    def test_team_analytics_endpoint(self):
        response = self.client.get('/api/reports/team-analytics/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('criteria_labels', response.data)
        self.assertIn('company_radar', response.data)
        self.assertIn('teams_radar', response.data)
        self.assertIn('distribution', response.data)

        # check distribution contains S, A, B, C, D
        grades = [g['grade'] for g in response.data['distribution']['grades']]
        self.assertEqual(grades, ['S', 'A', 'B', 'C', 'D'])

        # also test /api/admin/team-analytics/
        res_admin = self.client.get('/api/admin/team-analytics/')
        self.assertEqual(res_admin.status_code, 200)

    def test_dashboard_stats_endpoint(self):
        response = self.client.get('/api/reports/dashboard-stats/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('kpi', response.data)
        self.assertIn('team_averages', response.data)
        self.assertIn('team_grade_distribution', response.data)
        self.assertIn('criteria_team_radar', response.data)
        self.assertIn('score_table', response.data)

        # test direct /api/admin/dashboard-stats/
        res_admin = self.client.get('/api/admin/dashboard-stats/')
        self.assertEqual(res_admin.status_code, 200)

    def test_non_admin_cannot_read_reports_or_apply_bonus(self):
        self.client.force_authenticate(self.manager)

        self.assertEqual(self.client.get('/api/reports/dashboard-kpi/').status_code, 403)
        self.assertEqual(self.client.post(f'/api/teams/{self.team.pk}/bonus/', {'bonus_score': 1}, format='json').status_code, 403)
        self.assertEqual(self.client.get('/api/reports/team-analytics/').status_code, 403)
        self.assertEqual(self.client.get('/api/reports/dashboard-stats/').status_code, 403)