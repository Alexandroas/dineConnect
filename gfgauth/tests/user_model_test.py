from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time
from ..models import CustomUser, Business, businessHours
from Restaurant_handling.models import Cuisine, DieteryPreference

class CustomUserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123'
        }
        
    def test_create_user(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = CustomUser.objects.create_superuser(**self.user_data)
        self.assertTrue(admin.is_active)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_get_full_name(self):
        user = CustomUser.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), 'Test User')

    def test_email_unique(self):
        CustomUser.objects.create_user(**self.user_data)
        with self.assertRaises(Exception):
            CustomUser.objects.create_user(**self.user_data)

class BusinessModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='business@example.com',
            username='business',
            first_name='Business',
            last_name='Owner',
            password='testpass123'
        )
        
        self.business_data = {
            'business_name': 'Test Restaurant',
            'business_owner': self.user,
            'business_address': 'Test Address',
            'business_tax_code': '12345',
            'contact_number': '1234567890',
            'business_description': 'Test Description',
            'business_max_table_capacity': 4
        }

    def test_create_business(self):
        business = Business.objects.create(**self.business_data)
        self.assertEqual(business.business_name, self.business_data['business_name'])
        self.assertEqual(business.business_owner, self.user)

    def test_business_tax_code_unique(self):
        Business.objects.create(**self.business_data)
        self.business_data['contact_number'] = '0987654321'  # Change phone number to avoid unique constraint
        with self.assertRaises(Exception):
            Business.objects.create(**self.business_data)

    def test_get_average_rating_no_reviews(self):
        business = Business.objects.create(**self.business_data)
        self.assertEqual(business.get_average_rating(), 0)

    def test_business_hours(self):
        business = Business.objects.create(**self.business_data)
        hours = businessHours.objects.create(
            business=business,
            day_of_week=0,  # Monday
            opening_time=time(9, 0),  # 9 AM
            closing_time=time(17, 0),  # 5 PM
            shift_name='Regular Hours'
        )
        self.assertTrue(isinstance(hours, businessHours))
        self.assertEqual(str(hours), "Monday: 09:00 - 17:00")

class BusinessHoursModelTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='business@example.com',
            username='business',
            first_name='Business',
            last_name='Owner',
            password='testpass123'
        )
        
        self.business = Business.objects.create(
            business_name='Test Restaurant',
            business_owner=self.user,
            business_address='Test Address',
            business_tax_code='12345',
            contact_number='1234567890',
            business_description='Test Description'
        )

    def test_create_business_hours(self):
        hours = businessHours.objects.create(
            business=self.business,
            day_of_week=0,
            opening_time=time(9, 0),
            closing_time=time(17, 0),
            shift_name='Regular Hours'
        )
        self.assertEqual(hours.day_of_week, 0)
        self.assertEqual(hours.opening_time, time(9, 0))
        self.assertEqual(hours.closing_time, time(17, 0))

    def test_invalid_hours(self):
        with self.assertRaises(ValidationError):
            hours = businessHours(
                business=self.business,
                day_of_week=0,
                opening_time=time(17, 0),  # 5 PM
                closing_time=time(9, 0),   # 9 AM
                shift_name='Invalid Hours'
            )
            hours.full_clean()

    def test_overlapping_hours(self):
        # Create first set of hours
        businessHours.objects.create(
            business=self.business,
            day_of_week=0,
            opening_time=time(9, 0),
            closing_time=time(17, 0),
            shift_name='Regular Hours'
        )
        
        # Try to create overlapping hours
        with self.assertRaises(ValidationError):
            hours = businessHours(
                business=self.business,
                day_of_week=0,
                opening_time=time(12, 0),
                closing_time=time(20, 0),
                shift_name='Overlapping Hours'
            )
            hours.full_clean()

    def test_is_closed(self):
        hours = businessHours.objects.create(
            business=self.business,
            day_of_week=0,
            opening_time=time(9, 0),
            closing_time=time(17, 0),
            is_closed=True,
            shift_name='Closed Day'
        )
        self.assertEqual(str(hours), "Monday: Closed")