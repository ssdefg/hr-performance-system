from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class AuthenticationApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.get(employee_id='ADMIN')

    def test_login_returns_tokens_and_user_details(self):
        response = self.client.post(
            '/api/auth/login/',
            {'employee_id': 'ADMIN', 'password': 'admin1234!'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user'], {
            'employee_id': 'ADMIN',
            'name': 'ADMIN',
            'role': 'ADMIN',
            'team_id': None,
            'team_name': None,
        })

    def test_invalid_credentials_are_rejected(self):
        response = self.client.post(
            '/api/auth/login/',
            {'employee_id': 'ADMIN', 'password': 'incorrect'},
            format='json',
        )

        self.assertEqual(response.status_code, 401)

    def test_me_returns_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['employee_id'], 'ADMIN')
        self.assertEqual(response.data['role'], 'ADMIN')

    def test_default_admin_seed_is_idempotent(self):
        from apps.authentication.signals import seed_default_admin

        seed_default_admin(sender=get_user_model()._meta.app_config)
        self.assertEqual(get_user_model().objects.filter(employee_id='ADMIN').count(), 1)