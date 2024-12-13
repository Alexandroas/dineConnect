from django.utils import timezone
from datetime import datetime
from django.db import models

# Create your models here.
class Reservation(models.Model):
    reservation_id = models.AutoField(primary_key=True)
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    reservation_party_size = models.IntegerField()
    reservation_special_requests = models.TextField(max_length=100 , blank=True, null=True)
    business_id = models.ForeignKey('gfgauth.Business', on_delete=models.CASCADE)
    user_id = models.ForeignKey('gfgauth.CustomUser', on_delete=models.CASCADE)
    dish_id = models.ManyToManyField('Restaurant_handling.Dish', blank=True)
    RESERVATION_STATUS = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
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
            aware_datetime = timezone.make_aware(self.get_datetime)
            return aware_datetime > timezone.now()
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
    