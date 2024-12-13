from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.messages import get_messages
from reservations.models import Reservation
from gfgauth.models import Business, CustomUser, businessHours
from Restaurant_handling.models import Dish, DishType, Cuisine

class ReservationViewsTest(TestCase):
    def setUp(self):
        # Create test client
        self.client = Client()
        
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Create business owner
        self.business_owner = CustomUser.objects.create_user(
            username='business_owner',
            email='owner@example.com',
            password='testpass123'
        )
        
        # Create test business
        self.business = Business.objects.create(
            business_name='Test Restaurant',
            business_owner=self.business_owner,
            business_address='Test Address',
            business_tax_code='123456',
            business_max_table_capacity=4,
            contact_number='1234567890',
            business_description='Test Description'
        )

        for day in range(7):  # 0 = Monday to 6 = Sunday
            businessHours.objects.create(
            business=self.business,
            day_of_week=day,
            opening_time=datetime.strptime('09:00', '%H:%M').time(),
            closing_time=datetime.strptime('22:00', '%H:%M').time(),
            is_closed=False
        )
        # Login the test user
        self.client.login(username='testuser', password='testpass123')

    def test_make_reservation_get(self):
        """Test GET request to make reservation page"""
        response = self.client.get(
            reverse('reservations:restaurant_reservation', args=[self.business.business_id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservations/reservation.html')

    def test_make_reservation_post_success(self):
        """Test successful reservation creation"""
    # Get tomorrow's date and weekday
        future_date = timezone.now().date() + timedelta(days=1)
        weekday = future_date.weekday()  # 0 = Monday, 1 = Tuesday, etc.
        
        # Create business hours for the reservation day
        businessHours.objects.create(
            business=self.business,
            day_of_week=weekday,  # Set to match reservation day
            opening_time=datetime.strptime('09:00', '%H:%M').time(),
            closing_time=datetime.strptime('22:00', '%H:%M').time(),
            is_closed=False
        )

        data = {
            'reservation_date': future_date,
            'reservation_time': '14:00',  # Time within business hours
            'reservation_party_size': 2,
            'reservation_special_requests': 'No spicy food'
        }
        
        response = self.client.post(
            reverse('reservations:restaurant_reservation', args=[self.business.business_id]),
            data
        )
    
        # Print response and messages for debugging
        print("Response:", response.status_code)
        messages = list(get_messages(response.wsgi_request))
        for message in messages:
            print("Message:", message)

        # Check if reservation was created
        self.assertTrue(Reservation.objects.exists())
        reservation = Reservation.objects.first()
        self.assertEqual(reservation.reservation_status, 'Pending')
        self.assertEqual(reservation.reservation_party_size, 2)

    def test_make_reservation_invalid_date(self):
        """Test reservation with past date"""
        past_date = timezone.now().date() - timedelta(days=1)
        data = {
            'reservation_date': past_date,
            'reservation_time': '14:00',
            'reservation_party_size': 2
        }
        
        response = self.client.post(
            reverse('reservations:restaurant_reservation', args=[self.business.business_id]),
            data
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Reservation time cannot be in the past', str(messages[0]))

    def test_make_reservation_invalid_party_size(self):
        """Test reservation with party size exceeding maximum"""
        future_date = timezone.now().date() + timedelta(days=1)
        data = {
            'reservation_date': future_date,
            'reservation_time': '14:00',
            'reservation_party_size': 10  # Exceeds max capacity
        }
        
        response = self.client.post(
            reverse('reservations:restaurant_reservation', args=[self.business.business_id]),
            data
        )
        
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('Party size cannot exceed', str(messages[0]))

    def test_business_upcoming_reservations(self):
        """Test business owner viewing upcoming reservations"""
        # Login as business owner
        self.client.login(username='business_owner', password='testpass123')
        
        response = self.client.get(
            reverse('reservations:upcoming_reservations', args=[self.business.business_id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservations/upcoming_reservations.html')

    def test_reservation_details(self):
        """Test viewing reservation details"""
        # Create a test reservation
        reservation = Reservation.objects.create(
            reservation_date=timezone.now().date() + timedelta(days=1),
            reservation_time=datetime.strptime('14:00', '%H:%M').time(),
            reservation_party_size=2,
            business_id=self.business,
            user_id=self.user
        )
        
        # Login as business owner
        self.client.login(username='business_owner', password='testpass123')
        
        response = self.client.get(
            reverse('reservations:reservation_details', 
                   args=[self.business.business_id, reservation.reservation_id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservations/reservation_details.html')

    def test_cancel_reservation(self):
        """Test canceling a reservation"""
        # Create a test reservation
        reservation = Reservation.objects.create(
            reservation_date=timezone.now().date() + timedelta(days=1),
            reservation_time=datetime.strptime('14:00', '%H:%M').time(),
            reservation_party_size=2,
            business_id=self.business,
            user_id=self.user
        )
        
        # Login as business owner
        self.client.login(username='business_owner', password='testpass123')
        
        response = self.client.post(
            reverse('reservations:cancel_reservation', 
                   args=[self.business.business_id, reservation.reservation_id])
        )
        
        # Refresh reservation from database
        reservation.refresh_from_db()
        self.assertEqual(reservation.reservation_status, 'Cancelled')