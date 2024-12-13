from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Group
from ..models import Business, CustomUser
from reservations.models import Reservation
from django.utils import timezone  # Add this import
from datetime import timedelta    # Add this import
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
    
    
class AuthViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            password='testpass',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        super().setUp()
        app = SocialApp.objects.create(
        provider='google',
        name='Google',
        client_id='test-123456789-abcdef.apps.googleusercontent.com"',
        secret='test_secret_ABCDEF123456'
        )
        
        self.business_user = CustomUser.objects.create_user(
            username='testbusiness',
            password='testpass',
            email='business@example.com',
            first_name='Test',
            last_name='Business'
        )
        self.business_group = Group.objects.create(name='Business')
        self.business_user.groups.add(self.business_group)
        app.sites.add(Site.objects.get_current())

    def test_home_view(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gfgauth/home.html')

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('logout')
        response = self.client.get(url)
        self.assertRedirects(response, '/')
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_login_view(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gfgauth/login.html')

    def test_signup_view(self):
        url = reverse('signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gfgauth/signup.html')

    def test_password_change_view(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('password_change')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gfgauth/password_change.html')

    def test_profile_view(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('profile', args=['testuser'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gfgauth/profile.html')

    def test_view_reservation_view(self):
        reservation = Reservation.objects.create(
            user_id=self.user,
            business_id=Business.objects.create(
                business_name='Test Business',
                business_owner=self.business_user
            ),
            reservation_date='2023-06-15',
            reservation_time='12:00:00',
            reservation_party_size=2
        )
        self.client.login(username='testuser', password='testpass')
        url = reverse('view_reservation', args=[reservation.reservation_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gfgauth/view_reservation.html')

    def test_cancel_reservation_view(self):
        tomorrow = timezone.now().date() + timedelta(days=1)
    
        reservation = Reservation.objects.create(
        user_id=self.user,
        business_id=Business.objects.create(
            business_name='Test Business',
            business_owner=self.business_user
        ),
        reservation_date=tomorrow,
        reservation_time='12:00:00',
        reservation_party_size=2,
        reservation_status='Pending'
    )
        self.client.login(username='testuser', password='testpass')
        url = reverse('cancel_reservation', args=[reservation.reservation_id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('profile', kwargs={'username': 'testuser'}))
        
        updated_reservation = Reservation.objects.get(pk=reservation.pk)
        self.assertEqual(updated_reservation.reservation_status, 'Cancelled')