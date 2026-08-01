from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.dashboard_url = reverse('dashboard:home')
        
        # Create an existing user for login test
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='Password123!',
            role='DATA_SCIENTIST'
        )

    def test_user_registration_success(self):
        payload = {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'password1': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }
        response = self.client.post(self.register_url, payload)
        self.assertRedirects(response, self.dashboard_url)
        
        user_exists = User.objects.filter(username='newuser123').exists()
        self.assertTrue(user_exists)
        
        user = User.objects.get(username='newuser123')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.role, 'DATA_SCIENTIST')
        self.assertTrue(hasattr(user, 'profile'))

    def test_user_login_success(self):
        payload = {
            'username': 'existinguser',
            'password': 'Password123!'
        }
        response = self.client.post(self.login_url, payload)
        self.assertRedirects(response, self.dashboard_url)

    def test_user_login_invalid_password(self):
        payload = {
            'username': 'existinguser',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/email or password")

    def test_banned_user_login_denied(self):
        banned_user = User.objects.create_user(
            username='banneduser',
            email='banned@example.com',
            password='Password123!',
            is_banned=True
        )
        payload = {
            'username': 'banneduser',
            'password': 'Password123!'
        }
        response = self.client.post(self.login_url, payload)
        self.assertRedirects(response, self.login_url)
