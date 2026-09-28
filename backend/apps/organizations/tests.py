from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from apps.organizations.models import Team


class TeamManagementApiTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.get(employee_id='ADMIN')
        self.manager = get_user_model().objects.create_user(
            employee_id='M001', name='매니저', password='pass1234', role='MANAGER'
        )
        self.client.force_authenticate(self.admin)

    def test_admin_can_assign_only_one_team_to_manager(self):
        first = self.client.post('/api/teams/', {'name': '개발팀', 'manager_id': self.manager.pk}, format='json')
        second = self.client.post('/api/teams/', {'name': '기획팀', 'manager_id': self.manager.pk}, format='json')

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)

    def test_non_manager_cannot_be_assigned(self):
        response = self.client.post('/api/teams/', {'name': '운영팀', 'manager_id': self.admin.pk}, format='json')

        self.assertEqual(response.status_code, 400)

    def test_assigning_manager_syncs_user_team(self):
        response = self.client.post('/api/teams/', {
            'name': '인사팀', 'manager_id': self.manager.pk,
        }, format='json')
        self.manager.refresh_from_db()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.manager.team_id, response.data['id'])
        self.assertEqual(response.data['member_count'], 1)

    def test_updating_manager_assignment_syncs_user_team(self):
        team = Team.objects.create(name='미배정 팀')

        response = self.client.patch(f'/api/teams/{team.pk}/', {'manager_id': self.manager.pk}, format='json')
        self.manager.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.manager.team_id, team.pk)

    def test_non_admin_can_read_but_cannot_manage_teams(self):
        self.client.force_authenticate(self.manager)

        read_response = self.client.get('/api/teams/')
        write_response = self.client.post('/api/teams/', {'name': '비인가팀'}, format='json')

        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(write_response.status_code, 403)


class UserManagementApiTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.get(employee_id='ADMIN')
        self.client.force_authenticate(self.admin)

    def test_duplicate_employee_id_returns_bad_request(self):
        payload = {'employee_id': 'EMP1', 'name': '직원', 'password': 'pass1234', 'role': 'EMPLOYEE'}
        self.assertEqual(self.client.post('/api/users/', payload, format='json').status_code, 201)
        response = self.client.post('/api/users/', payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['employee_id'][0], '이미 사용 중인 사번입니다.')

    def test_created_password_is_hashed(self):
        response = self.client.post(
            '/api/users/',
            {'employee_id': 'EMP2', 'name': '직원2', 'password': 'pass1234', 'role': 'EMPLOYEE'},
            format='json',
        )
        user = get_user_model().objects.get(employee_id='EMP2')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(user.check_password('pass1234'))
        self.assertNotEqual(user.password, 'pass1234')

    def test_role_filter_returns_matching_users(self):
        get_user_model().objects.create_user(employee_id='EMP3', name='직원3', password='pass1234')

        response = self.client.get('/api/users/?role=EMPLOYEE')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(user['role'] == 'EMPLOYEE' for user in response.data))