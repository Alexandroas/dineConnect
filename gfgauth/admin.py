from django.contrib import admin

from Restaurant_handling.models import DieteryPreference

from . models import CustomUser, Business


from Restaurant_handling.admin import DishInline

class BusinessAdmin(admin.ModelAdmin):
    filter_horizontal = ('cuisine',)
    inlines = [DishInline]
class userAdmin(admin.ModelAdmin):
    filter_horizontal = ('groups', 'user_permissions')
    
admin.register(DieteryPreference)
class DieteryPreferenceAdmin(admin.ModelAdmin):
    filter_horizontal = ('dietery_name',)
    search_fields = ('dietery_name',)


admin.site.register(Business, BusinessAdmin)
admin.site.register(CustomUser, userAdmin)


