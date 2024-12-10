from django.db import models

class DieteryPreference(models.Model):
    dietery_id = models.AutoField(primary_key=True)
    dietery_name = models.CharField(max_length=100)
    def __str__(self):
        return self.dietery_name

class Cuisine(models.Model):
    cuisine_id = models.AutoField(primary_key=True)
    cuisine_name = models.CharField(max_length=100)
    def __str__(self):
        return self.cuisine_name 
    
class DishType(models.Model):
    dish_type_id = models.AutoField(primary_key=True)
    dish_type_name = models.CharField(max_length=100)
    def __str__(self):
        return self.dish_type_name
    
class Dish(models.Model):
    dish_id = models.AutoField(primary_key=True)
    dish_name = models.CharField(max_length=100)
    dish_cost = models.DecimalField(max_digits=10, decimal_places=2)
    dish_type = models.ForeignKey('DishType', on_delete=models.CASCADE)
    cuisine_id = models.ForeignKey('Cuisine', on_delete=models.CASCADE)
    business_id = models.ForeignKey('gfgauth.Business', on_delete=models.CASCADE)
    dish_description = models.TextField(max_length=100)
    dish_image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    allergens = models.ManyToManyField(DieteryPreference, blank=True, related_name='dishes')
    

    def __str__(self):
        return self.dish_name
    
    def get_allergens_display(self):
        return ", ".join([str(p) for p in self.allergens.all()])
        
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    review_rating = models.IntegerField()
    review_text = models.TextField(max_length=100)
    business_id = models.ForeignKey('gfgauth.Business', on_delete=models.CASCADE)
    user_id = models.ForeignKey('gfgauth.CustomUser', on_delete=models.CASCADE)
    
    def __str__(self):
        return str (self.review_id)