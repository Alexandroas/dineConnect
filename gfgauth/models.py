from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from Restaurant_handling.models import Cuisine, DieteryPreference


# Regular User Model
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=24)
    username = models.CharField(max_length=24, unique=True)
    last_name = models.CharField(max_length=24)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        blank=True, 
        null=True
    )
    favourite_restaurants = models.ManyToManyField(
        'Business', 
        blank=True, 
        related_name='favourite_users')
    #TODO: Add restaurant favourite field
    dietery_preference = models.ManyToManyField(
        DieteryPreference, 
        blank=True, 
        related_name='users'
    )
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return self.email

class Business(models.Model):
    business_id = models.AutoField(primary_key=True)
    business_name = models.CharField(max_length=100)
    business_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='businesses'
    )
    business_address = models.TextField(max_length=255)
    business_tax_code = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    business_description = models.TextField(max_length=255)
    cuisine = models.ManyToManyField(
        Cuisine, 
        blank=True, 
        related_name='businesses'
    )
    business_image = models.ImageField(
        upload_to='businesses/', 
        blank=True, 
        null=True
    )
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        verbose_name = 'business'
        verbose_name_plural = 'businesses'
        ordering = ['business_name']

    def __str__(self):
        return self.business_name

    def get_cuisines(self):
        """Return all cuisines for this business"""
        return self.cuisine.all()

    def get_cuisine_names(self):
        """Return cuisine names as comma-separated string"""
        return ", ".join([cuisine.cuisine_name for cuisine in self.cuisine.all()])

    def is_open(self, check_time=None):
        """
        Check if business is open at a specific time
        If no time provided, checks current time
        """
        if check_time is None:
            check_time = timezone.localtime().time()
        
        if self.opening_time <= self.closing_time:
            return self.opening_time <= check_time <= self.closing_time
        else:  # Handles cases where closing time is after midnight
            return check_time >= self.opening_time or check_time <= self.closing_time

    def get_available_time_slots(self, date):
        """
        Return available time slots for reservations on a given date
        """
        from Restaurant_handling.models import Reservation  # Import here to avoid circular import
        
        # Convert opening and closing times to datetime objects for the given date
        opening_datetime = datetime.combine(date, self.opening_time)
        closing_datetime = datetime.combine(date, self.closing_time)
        
        # Create 30-minute time slots
        time_slots = []
        current_slot = opening_datetime
        while current_slot < closing_datetime:
            # Get existing reservations for this time slot
            existing_reservations = Reservation.objects.filter(
                business_id=self,
                reservation_date=date,
                reservation_time=current_slot.time()
            ).count()
            
            # Assuming max 4 reservations per time slot
            if existing_reservations < 4:
                time_slots.append(current_slot.time())
            
            current_slot += timedelta(minutes=30)
        
        return time_slots

    def get_upcoming_reservations(self):
        """Get all upcoming reservations for this business"""
        current_datetime = timezone.now()
        return self.reservation_set.filter(
            models.Q(reservation_date__gt=current_datetime.date()) |
            models.Q(
                reservation_date=current_datetime.date(),
                reservation_time__gt=current_datetime.time()
            )
        ).order_by('reservation_date', 'reservation_time')

    def get_past_reservations(self):
        """Get all past reservations for this business"""
        current_datetime = timezone.now()
        return self.reservation_set.filter(
            models.Q(reservation_date__lt=current_datetime.date()) |
            models.Q(
                reservation_date=current_datetime.date(),
                reservation_time__lte=current_datetime.time()
            )
        ).order_by('-reservation_date', '-reservation_time')

    def get_today_reservations(self):
        """Get all reservations for today"""
        today = timezone.now().date()
        return self.reservation_set.filter(
            reservation_date=today
        ).order_by('reservation_time')

    def get_reservation_stats(self):
        """Get basic statistics about reservations"""
        total_reservations = self.reservation_set.count()
        upcoming_reservations = self.get_upcoming_reservations().count()
        today_reservations = self.get_today_reservations().count()
        
        return {
            'total': total_reservations,
            'upcoming': upcoming_reservations,
            'today': today_reservations
        }
