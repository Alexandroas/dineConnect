from django import forms
from .models import Testimonial

class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['content', 'rating']  # Add any other fields you want users to fill
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with DineConnect...',
                'rows': 4
            }),
            'rating': forms.Select(attrs={'class': 'form-control'})
        }