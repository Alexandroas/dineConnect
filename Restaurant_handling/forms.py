from django import forms
from .models import Dish, Reservation





class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['dish_name', 'dish_cost', 'dish_description', 'dish_image', 'dish_type', 'cuisine_id']
        exlude = ['buisness_id']
        
class DishUpdateForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ['dish_name', 'dish_cost', 'dish_description', 'dish_image', 'dish_type', 'cuisine_id']
        exlude = ['buisness_id']
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['reservation_date', 'reservation_time', 'reservation_party_size', 'reservation_special_requests']
        exclude = ['business_id', 'user_id', 'reservation_status']