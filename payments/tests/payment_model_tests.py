from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from unittest.mock import patch, MagicMock
import stripe # type: ignore
import json
from payments.models import Payment
from reservations.models import Reservation
from gfgauth.models import Business
from django.utils import timezone

class PaymentModelTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.business = Business.objects.create(
            business_name='Test Restaurant',
            business_owner=self.user,
            business_id=12345
        )
        self.reservation = Reservation.objects.create(
            user_id=self.user,
            business_id=self.business,
            reservation_date=timezone.now().date(),
            reservation_time=timezone.now().time(),
            reservation_party_size=2,
            reservation_status='Pending'
        )
        self.payment = Payment.objects.create(
            reservation=self.reservation,
            amount=Decimal('50.00'),
            stripe_payment_intent_id='pi_test123',
            user=self.user,
            business=self.business,
            status='pending'
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.amount, Decimal('50.00'))
        self.assertEqual(self.payment.status, 'pending')
        self.assertEqual(str(self.payment), f"Payment for Reservation {self.reservation.reservation_id}")

    def test_payment_status_choices(self):
        valid_statuses = ['pending', 'succeeded', 'failed', 'refunded']
        for status in valid_statuses:
            self.payment.status = status
            self.payment.save()
            self.assertEqual(self.payment.status, status)

class PaymentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.business = Business.objects.create(
            business_name='Test Restaurant',
            business_owner=self.user,
            business_id=12345
        )
        self.reservation = Reservation.objects.create(
            user_id=self.user,
            business_id=self.business,
            reservation_date=timezone.now().date(),
            reservation_time=timezone.now().time(),
            reservation_party_size=2,
            reservation_status='Pending'
        )
        self.client.login(email='test@example.com', password='testpass123')

        # Add dish to reservation to test total amount calculation
        class MockDish:
            dish_cost = Decimal('25.00')
        self.reservation.dish_id.add = MagicMock(return_value=[MockDish()])

    @patch('stripe.PaymentIntent.create')
    def test_payment_view_get(self, mock_create):
        mock_create.return_value = MagicMock(client_secret='test_secret')
        url = reverse('payments:payment', kwargs={'reservation_id': self.reservation.reservation_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/payment.html')

    @patch('stripe.PaymentIntent.create')
    def test_payment_view_post(self, mock_create):
        mock_create.return_value = MagicMock(client_secret='test_secret')
        url = reverse('payments:payment', kwargs={'reservation_id': self.reservation.reservation_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/payment.html')

    @patch('stripe.PaymentIntent.create')
    def test_payment_view_stripe_error(self, mock_create):
        # Create a proper Stripe error mock
        error = stripe.error.StripeError('Test error')
        error.error = MagicMock()
        error.error.message = 'Test error'
        mock_create.side_effect = error
        
        url = reverse('payments:payment', kwargs={'reservation_id': self.reservation.reservation_id})
        response = self.client.post(url)

        # Use message middleware if you want to test for error messages
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Payment error: Test error')
        
        # Check redirection to the proper URL
        expected_url = reverse('reservations:reservation_details', kwargs={
            'business_id': self.business.business_id,
            'reservation_id': self.reservation.reservation_id
        })
        self.assertRedirects(response, expected_url)

    @patch('stripe.PaymentIntent.create')
    def test_process_payment_success(self, mock_create):
        mock_create.return_value = MagicMock(
            id='pi_test123',
            status='succeeded'
        )
        url = reverse('payments:process_payment', kwargs={'reservation_id': self.reservation.reservation_id})
        response = self.client.post(
            url,
            data=json.dumps({'payment_method_id': 'pm_test123'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

    @patch('stripe.PaymentIntent.create')
    def test_process_payment_card_error(self, mock_create):
        # Create a proper card error mock
        error = stripe.error.CardError(
            message="Your card was declined",
            param="card_number",
            code="card_declined",
        )
        error.error = MagicMock()
        error.error.message = "Your card was declined"
        mock_create.side_effect = error
        
        url = reverse('payments:process_payment', kwargs={'reservation_id': self.reservation.reservation_id})
        response = self.client.post(
            url,
            data=json.dumps({'payment_method_id': 'pm_test123'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], "Your card was declined")

class PaymentHistoryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.User = get_user_model()
        self.user = self.User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.business = Business.objects.create(
            business_name='Test Restaurant',
            business_owner=self.user,
            business_id=12345
        )
        self.client.login(email='test@example.com', password='testpass123')

        self.reservation = Reservation.objects.create(
            user_id=self.user,
            business_id=self.business,
            reservation_date=timezone.now().date(),
            reservation_time=timezone.now().time(),
            reservation_party_size=2,
            reservation_status='Pending'
        )

    def test_payment_history_view(self):
        url = reverse('payments:payment_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/payment_history.html')

    def test_business_payment_history_view(self):
        url = reverse('payments:business_payment_history', kwargs={'business_id': self.business.business_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/business_payment_history.html')

    def test_business_payment_history_stats(self):
        Payment.objects.create(
            reservation=self.reservation,
            amount=Decimal('50.00'),
            stripe_payment_intent_id='pi_test123',
            user=self.user,
            business=self.business,
            status='succeeded'
        )
        Payment.objects.create(
            reservation=self.reservation,
            amount=Decimal('75.00'),
            stripe_payment_intent_id='pi_test124',
            user=self.user,
            business=self.business,
            status='succeeded'
        )
        
        url = reverse('payments:business_payment_history', kwargs={'business_id': self.business.business_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_revenue'], Decimal('125.00'))
        self.assertEqual(response.context['successful_payments'], 2)