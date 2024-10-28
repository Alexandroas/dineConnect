from django.contrib import admin

from . models import CustomUser, Business


from Restaurant_handling.admin import DishInline

class BusinessAdmin(admin.ModelAdmin):
    filter_horizontal = ('cuisine',)
    inlines = [DishInline]
class userAdmin(admin.ModelAdmin):
    filter_horizontal = ('groups', 'user_permissions')
    

    

admin.site.register(Business, BusinessAdmin)
admin.site.register(CustomUser, userAdmin)


