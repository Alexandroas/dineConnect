from django.db import models
from reservations.models import Reservation
# Create your models here.
class Payment(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=200)
    status = models.CharField(max_length=100, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Reservation {self.reservation.reservation_id}"