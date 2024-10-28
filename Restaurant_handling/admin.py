from django.contrib import admin
from .models import Cuisine, Dish, DishType, Reservation


# Register the Cuisine model
 # This provides a horizontal filter widget to select multiple cuisines


admin.site.register(Cuisine)

class DishInline(admin.TabularInline):
    model = Dish
    extra = 1  # Number of extra forms to display

class CuisineAdmin(admin.ModelAdmin):
    inlines = [DishInline]
# Register the Dish model if needed
admin.site.register(Dish)
admin.site.register(DishType)
admin.site.register(Reservation)