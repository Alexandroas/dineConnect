from django import forms
from .models import DieteryPreference, Dish, Review

class DishForm(forms.ModelForm):
    allergens = forms.ModelMultipleChoiceField(
        queryset=DieteryPreference.objects.all(),
        widget = forms.CheckboxSelectMultiple(attrs={
            'class': 'form-control'
        }),
        required=False,
        label='Allergens/Dietery restrictions'
    )
    class Meta:
        model = Dish
        fields = ['dish_name', 'dish_cost', 'dish_description', 'dish_image', 'dish_type', 'cuisine_id', 'allergens']
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
    allergens = forms.ModelMultipleChoiceField(
        queryset=DieteryPreference.objects.all(),
        widget = forms.CheckboxSelectMultiple(attrs={
            'class': 'form-control'
        }),
        required=False,
        label='Allergens/Dietery restrictions'
    )

    class Meta:
        model = Dish
        fields = ['dish_name', 'dish_cost', 'is_available', 'dish_description', 
                 'dish_image', 'dish_type', 'cuisine_id', 'allergens']
        exclude = ['business_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['is_available'].initial = self.instance.is_available
            self.fields['allergens'].initial = self.instance.allergens.all()
        
    def clean_is_available(self):
        return self.cleaned_data['is_available'] == 'True'

class ReviewForm(forms.ModelForm):
    review_rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={
            'class': 'hidden peer'
        })
    )
    
    review_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Share your experience...',
            'rows': 4
        }),
        required=True
    )

    class Meta:
        model = Review
        fields = ['review_rating', 'review_text']