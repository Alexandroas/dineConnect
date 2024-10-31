from django import forms
from .models import Dish, Reservation





class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['dish_name', 'dish_cost', 'dish_description', 'dish_image', 'dish_type', 'cuisine_id']
        exlude = ['buisness_id']
        
class DishUpdateForm(forms.ModelForm):
    AVAILABILITY_CHOICES = [
        (True, 'Available'),
        (False, 'Unavailable')
    ]
    
    is_available = forms.ChoiceField(
        choices=AVAILABILITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=True,
        label='Availability Status'
    )

    class Meta:
        model = Dish
        fields = ['dish_name', 'dish_cost', 'is_available', 'dish_description', 
                 'dish_image', 'dish_type', 'cuisine_id']
        exclude = ['business_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['is_available'].initial = self.instance.is_available
        
    def clean_is_available(self):
        return self.cleaned_data['is_available'] == 'True'
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['reservation_date', 'reservation_time', 'reservation_party_size', 'reservation_special_requests']
        exclude = ['business_id', 'user_id', 'reservation_status']