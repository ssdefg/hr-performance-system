from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.evaluations.models import EvaluationCriteria, EvaluationItemScore, EvaluationReview
from apps.organizations.models import Team


class EvaluationCriteriaApiTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.get(employee_id='ADMIN')
        self.client.force_authenticate(self.admin)

    def test_criteria_crud_and_weight_summary(self):
        first = self.client.post('/api/evaluations/criteria/', {
            'name': '직무 역량', 'description': '업무 전문성', 'weight': 40, 'order': 1,
        }, format='json')
        self.assertEqual(first.status_code, 201)
        second = self.client.post('/api/evaluations/criteria/', {
            'name': '협업', 'weight': 60, 'order': 2,
        }, format='json')
        self.assertEqual(second.status_code, 201)

        summary = self.client.get('/api/evaluations/criteria/summary/')
        self.assertEqual(summary.data, {'criteria_count': 2, 'total_weight': 100, 'is_valid': True})

        self.client.patch(f"/api/evaluations/criteria/{second.data['id']}/", {'weight': 70}, format='json')
        summary = self.client.get('/api/evaluations/criteria/summary/')
        self.assertEqual(summary.data['total_weight'], 110)
        self.assertFalse(summary.data['is_valid'])

    def test_weight_out_of_range_is_rejected(self):
        response = self.client.post('/api/evaluations/criteria/', {
            'name': '잘못된 항목', 'weight': 101, 'order': 1,
        }, format='json')

        self.assertEqual(response.status_code, 400)

    def test_non_admin_can_read_but_cannot_modify_criteria(self):
        EvaluationCriteria.objects.create(name='기존 항목', weight=100)
        employee = get_user_model().objects.create_user(employee_id='EMP4', name='직원', password='pass1234')
        self.client.force_authenticate(employee)

        self.assertEqual(self.client.get('/api/evaluations/criteria/').status_code, 200)
        self.assertEqual(self.client.post('/api/evaluations/criteria/', {'name': '신규', 'weight': 1}, format='json').status_code, 403)


class ManagerEvaluationApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.manager = user_model.objects.create_user(
            employee_id='M100', name='매니저', password='pass1234', role='MANAGER'
        )
        self.team = Team.objects.create(name='평가팀', manager=self.manager)
        self.manager.team = self.team
        self.manager.save(update_fields=['team'])
        self.employee = user_model.objects.create_user(
            employee_id='E100', name='평가 대상', password='pass1234', role='EMPLOYEE', team=self.team
        )
        self.other_team = Team.objects.create(name='다른 팀')
        self.outsider = user_model.objects.create_user(
            employee_id='E200', name='타 팀 직원', password='pass1234', role='EMPLOYEE', team=self.other_team
        )
        self.criteria = [
            EvaluationCriteria.objects.create(name='역량', weight=40, order=1),
            EvaluationCriteria.objects.create(name='협업', weight=60, order=2),
        ]
        self.client.force_authenticate(self.manager)

    def test_manager_sees_only_own_team_members(self):
        response = self.client.get('/api/evaluations/team-members/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['team_name'], '평가팀')
        self.assertEqual([member['employee_id'] for member in response.data['members']], ['E100'])
        self.assertEqual(response.data['members'][0]['review_status'], 'NOT_STARTED')

    def test_manager_cannot_read_or_save_other_team_employee(self):
        read_response = self.client.get(f'/api/evaluations/reviews/{self.outsider.employee_id}/')
        save_response = self.client.post(
            f'/api/evaluations/reviews/{self.outsider.employee_id}/draft/',
            {'scores': []},
            format='json',
        )

        self.assertEqual(read_response.status_code, 404)
        self.assertEqual(save_response.status_code, 404)

    def test_draft_is_restored_and_score_is_calculated(self):
        payload = {'scores': [{'criteria_id': self.criteria[0].id, 'score': 4}]}
        save_response = self.client.post(
            f'/api/evaluations/reviews/{self.employee.employee_id}/draft/', payload, format='json'
        )
        read_response = self.client.get(f'/api/evaluations/reviews/{self.employee.employee_id}/')

        self.assertEqual(save_response.status_code, 200)
        self.assertEqual(save_response.data['raw_score'], 32.0)
        self.assertEqual(read_response.data['status'], 'DRAFT')
        self.assertEqual(read_response.data['scores'][0]['score'], 4)

    def test_submit_requires_all_criteria_and_locks_after_submission(self):
        incomplete = self.client.post(
            f'/api/evaluations/reviews/{self.employee.employee_id}/submit/',
            {'scores': [{'criteria_id': self.criteria[0].id, 'score': 5}]},
            format='json',
        )
        self.assertEqual(incomplete.status_code, 400)

        payload = {'scores': [
            {'criteria_id': self.criteria[0].id, 'score': 5},
            {'criteria_id': self.criteria[1].id, 'score': 5},
        ]}
        submitted = self.client.post(
            f'/api/evaluations/reviews/{self.employee.employee_id}/submit/', payload, format='json'
        )
        locked = self.client.post(
            f'/api/evaluations/reviews/{self.employee.employee_id}/draft/', payload, format='json'
        )

        self.assertEqual(submitted.status_code, 200)
        self.assertEqual(submitted.data['status'], 'SUBMITTED')
        self.assertEqual(submitted.data['raw_score'], 100.0)
        self.assertEqual(locked.status_code, 403)


class EmployeeReviewApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.manager = user_model.objects.create_user(
            employee_id='M200', name='평가 매니저', password='pass1234', role='MANAGER'
        )
        self.team = Team.objects.create(name='직원 조회 팀', manager=self.manager)
        self.employee = user_model.objects.create_user(
            employee_id='E300', name='본인', password='pass1234', role='EMPLOYEE', team=self.team
        )
        self.other_employee = user_model.objects.create_user(
            employee_id='E301', name='다른 직원', password='pass1234', role='EMPLOYEE', team=self.team
        )
        criteria = EvaluationCriteria.objects.create(name='성과', weight=100, order=1)
        review = EvaluationReview.objects.create(
            employee=self.employee,
            evaluator=self.manager,
            status='SUBMITTED',
            raw_score=80,
            final_score=83.5,
        )
        EvaluationItemScore.objects.create(review=review, criteria=criteria, score=4)
        self.client.force_authenticate(self.employee)

    def test_employee_sees_only_own_submitted_result(self):
        response = self.client.get('/api/evaluations/my-review/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['employee_id'], self.employee.employee_id)
        self.assertEqual(response.data['scores'][0]['earned_score'], 80.0)
        self.assertEqual(response.data['final_score'], 83.5)

    def test_employee_without_submitted_review_sees_in_progress(self):
        self.client.force_authenticate(self.other_employee)

        response = self.client.get('/api/evaluations/my-review/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'IN_PROGRESS')
