from django.db import models
from gfgauth.models import CustomUser

# Create your models here.
class Testimonial(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='testimonial')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Optional fields you might want to add:
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return f"Testimonial by {self.user.username}"