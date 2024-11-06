from django.db import models
from django.utils import timezone
from datetime import datetime


class DieteryPreference(models.Model):
    dietery_id = models.AutoField(primary_key=True)
    dietery_name = models.CharField(max_length=100)
    def __str__(self):
        return self.dietery_name

class Cuisine(models.Model):
    cuisine_id = models.AutoField(primary_key=True)
    cuisine_name = models.CharField(max_length=100)
    def __str__(self):
        return self.cuisine_name 
    
class DishType(models.Model):
    dish_type_id = models.AutoField(primary_key=True)
    dish_type_name = models.CharField(max_length=100)
    def __str__(self):
        return self.dish_type_name
    
class Dish(models.Model):
    dish_id = models.AutoField(primary_key=True)
    dish_name = models.CharField(max_length=100)
    dish_cost = models.DecimalField(max_digits=10, decimal_places=2)
    dish_type = models.ForeignKey('DishType', on_delete=models.CASCADE)
    cuisine_id = models.ForeignKey('Cuisine', on_delete=models.CASCADE)
    business_id = models.ForeignKey('gfgauth.Business', on_delete=models.CASCADE)
    dish_description = models.TextField(max_length=100)
    dish_image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    

    def __str__(self):
        return self.dish_name
    

class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    reservation_party_size = models.IntegerField()
    reservation_special_requests = models.TextField(max_length=100 , blank=True, null=True)
    business_id = models.ForeignKey('gfgauth.Business', on_delete=models.CASCADE)
    user_id = models.ForeignKey('gfgauth.CustomUser', on_delete=models.CASCADE)
    dish_id = models.ManyToManyField('Dish', blank=True)
    RESERVATION_STATUS = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
    ]
    reservation_status = models.CharField(
        max_length=20,
        choices=RESERVATION_STATUS,
        default='Pending'
    )
    @property
    def get_datetime(self):
        """Combine date and time into a datetime object"""
        if self.reservation_date and self.reservation_time:
            return datetime.combine(self.reservation_date, self.reservation_time)
        return None
    
    @property
    def is_upcoming(self):
        if self.get_datetime:
            return self.get_datetime > timezone.now()
        return False

    @classmethod
    def upcoming_reservations(cls):
        current_datetime = timezone.now()
        return cls.objects.filter(
            reservation_date__gte=current_datetime.date()
        ).filter(
            models.Q(reservation_date__gt=current_datetime.date()) |
            models.Q(
                reservation_date=current_datetime.date(),
                reservation_time__gt=current_datetime.time()
            )
        )

    @classmethod
    def past_reservations(cls):
        current_datetime = timezone.now()
        return cls.objects.filter(
            models.Q(reservation_date__lt=current_datetime.date()) |
            models.Q(
                reservation_date=current_datetime.date(),
                reservation_time__lte=current_datetime.time()
            )
        )

    def __str__(self):
        return f"Reservation for {self.user_id.username} at {self.business_id.business_name} - {str(self.reservation_date)}"

# Restaurant_handling/models.py
from django.db import models

class Payment(models.Model):
    reservation = models.ForeignKey('Reservation', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=200)
    status = models.CharField(max_length=100, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Reservation {self.reservation.reservation_id}"
        
"""class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    review_rating = models.IntegerField()
    review_text = models.TextField(max_length=100)
    business_id = models.ForeignKey('gfgauth.Business', on_delete=models.CASCADE)
    user_id = models.ForeignKey('gfgauth.User', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.review_id """