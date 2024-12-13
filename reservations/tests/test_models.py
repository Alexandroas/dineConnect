from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from reservations.models import Reservation
from gfgauth.models import Business, CustomUser
from Restaurant_handling.models import Dish

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from reservations.models import Reservation
from gfgauth.models import Business, CustomUser, businessHours
from Restaurant_handling.models import Dish, DishType, Cuisine

class ReservationModelTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create test business
        self.business = Business.objects.create(
            business_name='Test Restaurant',
            business_owner=self.user,
            business_address='Test Address',
            business_tax_code='123456',
            business_max_table_capacity=4,
            contact_number='1234567890',
            business_description='Test Description'
        )

        # Create business hours with timezone-aware time
        current_tz = timezone.get_current_timezone()
        opening_time = timezone.datetime.strptime('09:00', '%H:%M').time()
        closing_time = timezone.datetime.strptime('22:00', '%H:%M').time()
        
        self.business_hours = businessHours.objects.create(
            business=self.business,
            day_of_week=1,  # Monday
            opening_time=opening_time,
            closing_time=closing_time,
            is_closed=False,
            shift_name='Regular Hours'
        )

        # Create test cuisine and dish type
        self.cuisine = Cuisine.objects.create(
            cuisine_name='Test Cuisine'
        )
        
        self.dish_type = DishType.objects.create(
            dish_type_name='Test Type'
        )

        # Create a test reservation with timezone-aware datetime
        self.future_date = timezone.now().date() + timedelta(days=1)
        self.future_time = timezone.datetime.strptime('14:00', '%H:%M').time()
        
        self.reservation = Reservation.objects.create(
            reservation_date=self.future_date,
            reservation_time=self.future_time,
            reservation_party_size=2,
            business_id=self.business,
            user_id=self.user,
            reservation_special_requests='No spicy food'
        )

    def test_basic_reservation_creation(self):
        """Test basic reservation creation with required fields"""
        self.assertEqual(self.reservation.reservation_status, 'Pending')
        self.assertEqual(self.reservation.reservation_party_size, 2)
        self.assertEqual(self.reservation.business_id, self.business)
        self.assertEqual(self.reservation.user_id, self.user)
        self.assertTrue(self.reservation.reservation_id)

    def test_reservation_string_representation(self):
        """Test the string representation of the reservation"""
        expected_string = f"Reservation for testuser at Test Restaurant - {str(self.future_date)}"
        self.assertEqual(str(self.reservation), expected_string)

    def test_get_datetime_property(self):
        """Test the get_datetime property"""
        expected_datetime = datetime.combine(self.future_date, self.future_time)
        self.assertEqual(self.reservation.get_datetime, expected_datetime)

    def test_is_upcoming_property(self):
        """Test is_upcoming property for future and past reservations"""
        # Future reservation should be upcoming
        self.assertTrue(self.reservation.is_upcoming)
        
        # Past reservation should not be upcoming
        past_date = timezone.now().date() - timedelta(days=1)
        past_time = timezone.datetime.strptime('14:00', '%H:%M').time()
        past_reservation = Reservation.objects.create(
            reservation_date=past_date,
            reservation_time=past_time,
            reservation_party_size=2,
            business_id=self.business,
            user_id=self.user
        )
        self.assertFalse(past_reservation.is_upcoming)

    def test_upcoming_reservations_classmethod(self):
        """Test the upcoming_reservations class method"""
        # Create a past reservation
        past_date = timezone.now().date() - timedelta(days=1)
        past_reservation = Reservation.objects.create(
            reservation_date=past_date,
            reservation_time=self.future_time,
            reservation_party_size=2,
            business_id=self.business,
            user_id=self.user
        )
        
        upcoming = Reservation.upcoming_reservations()
        self.assertIn(self.reservation, upcoming)
        self.assertNotIn(past_reservation, upcoming)

    def test_past_reservations_classmethod(self):
        """Test the past_reservations class method"""
        # Create a past reservation
        past_date = timezone.now().date() - timedelta(days=1)
        past_reservation = Reservation.objects.create(
            reservation_date=past_date,
            reservation_time=self.future_time,
            reservation_party_size=2,
            business_id=self.business,
            user_id=self.user
        )
        
        past = Reservation.past_reservations()
        self.assertIn(past_reservation, past)
        self.assertNotIn(self.reservation, past)

    def test_reservation_status_transitions(self):
        """Test reservation status transitions"""
        # Test initial status
        self.assertEqual(self.reservation.reservation_status, 'Pending')
        
        # Test status update to Confirmed
        self.reservation.reservation_status = 'Confirmed'
        self.reservation.save()
        self.assertEqual(self.reservation.reservation_status, 'Confirmed')
        
        # Test status update to Completed
        self.reservation.reservation_status = 'Completed'
        self.reservation.save()
        self.assertEqual(self.reservation.reservation_status, 'Completed')

    def test_special_requests(self):
        """Test special requests field"""
        # Test with special requests
        self.assertEqual(self.reservation.reservation_special_requests, 'No spicy food')
        
        # Test without special requests
        reservation_no_requests = Reservation.objects.create(
            reservation_date=self.future_date,
            reservation_time=self.future_time,
            reservation_party_size=2,
            business_id=self.business,
            user_id=self.user
        )
        self.assertIsNone(reservation_no_requests.reservation_special_requests)

    def test_dish_relationships(self):
        """Test many-to-many relationship with dishes"""
        # Create test dishes
        dish1 = Dish.objects.create(
            dish_name='Test Dish 1',
            dish_cost=10.00,
            business_id=self.business,
            dish_description='Test Description 1',
            dish_type=self.dish_type,
            cuisine_id=self.cuisine
        )
        dish2 = Dish.objects.create(
            dish_name='Test Dish 2',
            dish_cost=15.00,
            business_id=self.business,
            dish_description='Test Description 2',
            dish_type=self.dish_type,
            cuisine_id=self.cuisine
        )
        # Add dishes to reservation
        self.reservation.dish_id.add(dish1, dish2)
        
        # Test dish relationships
        self.assertEqual(self.reservation.dish_id.count(), 2)
        self.assertIn(dish1, self.reservation.dish_id.all())
        self.assertIn(dish2, self.reservation.dish_id.all())