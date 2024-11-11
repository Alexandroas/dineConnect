from django import forms
from .models import Reservation


class ReservationForm(forms.ModelForm):
    reservation_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'dateinput'
            }
        )
    )
    
    reservation_time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                'type': 'time',
                'class': 'timeinput'
            }
        )
    )

    class Meta:
        model = Reservation
        fields = ['reservation_date', 'reservation_time', 'reservation_party_size', 'reservation_special_requests']
        exclude = ['business_id', 'user_id', 'reservation_status']