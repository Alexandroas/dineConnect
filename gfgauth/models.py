from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from Restaurant_handling.models import Cuisine, DieteryPreference
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


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
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

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
    def get_reservation_users_with_stats(self):
        """
        Return users with their reservation statistics for this business
        Returns a list of dictionaries containing user info and their reservation counts
        """
        from django.db.models import Count
        return CustomUser.objects.filter(
            reservation__business_id=self
        ).annotate(
            total_reservations=Count('reservation'),
            pending_reservations=Count(
                'reservation',
                filter=models.Q(reservation__reservation_status='Pending')
            ),
            confirmed_reservations=Count(
                'reservation',
                filter=models.Q(reservation__reservation_status='Confirmed')
            ),
            cancelled_reservations=Count(
                'reservation',
                filter=models.Q(reservation__reservation_status='Cancelled')
            )
        ).distinct()

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
    def is_open(self, check_datetime=None):
        """Check if business is open at a specific datetime"""
        if check_datetime is None:
            check_datetime = timezone.localtime()
        
        return self.business_hours.filter(
            day_of_week=check_datetime.weekday(),
            opening_time__lte=check_datetime.time(),
            closing_time__gte=check_datetime.time(),
            is_closed=False
        ).exists()

class businessHours(models.Model):
        DAYS_OF_WEEK = [
            (0, _('Monday')),
            (1, _('Tuesday')),
            (2, _('Wednesday')),
            (3, _('Thursday')),
            (4, _('Friday')),
            (5, _('Saturday')),
            (6, _('Sunday')),
        ]
        business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='business_hours'
    )
        day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
        opening_time = models.TimeField()
        closing_time = models.TimeField()
        is_closed = models.BooleanField(default=False)
        shift_name = models.CharField(
            max_length=50,
            blank=True,
            help_text="Optional name for this shift (e.g., 'Lunch', 'Dinner')"
        )

class Meta:
    verbose_name = 'business hours'
    verbose_name_plural = 'business hours'
    ordering = ['day_of_week', 'opening_time']
    # Ensure we don't have overlapping hours for the same business/day
    constraints = [
        models.UniqueConstraint(
            fields=['business', 'day_of_week', 'shift_name'],
            name='unique_business_hours_shift'
        )
    ]

    def clean(self):
        """Validate that closing time is after opening time"""
        if self.opening_time and self.closing_time:
            if self.closing_time <= self.opening_time:
                raise ValidationError(
                    _('Closing time must be after opening time')
                )
            
            # Check for overlapping hours on the same day
            overlapping = businessHours.objects.filter(
                business=self.business,
                day_of_week=self.day_of_week,
                is_closed=False
            ).exclude(pk=self.pk).filter(
                models.Q(opening_time__lte=self.closing_time,
                        closing_time__gte=self.opening_time)
            )
            
            if overlapping.exists():
                raise ValidationError(
                    _('Hours overlap with existing business hours for this day')
                )

    def __str__(self):
        day_name = self.get_day_of_week_display()
        if self.is_closed:
            return f"{day_name}: Closed"
        return f"{day_name}: {self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
def get_buisness_hours(self):
    """
    Return business hours as a dictionary
    """
    hours = {}
    for hour in self.business_hours.all():
        day_name = hour.get_day_of_week_display()
        if hour.is_closed:
            hours[day_name] = 'Closed'
        else:
            hours[day_name] = f"{hour.opening_time.strftime('%H:%M')} - {hour.closing_time.strftime('%H:%M')}"
    
    return hours