# gfgauth/management/commands/create_sample_menus.py

from django.core.management.base import BaseCommand
from gfgauth.models import Business
from Restaurant_handling.models import Dish
import random

class Command(BaseCommand):
    help = 'Creates sample menu items for each restaurant'

    def handle(self, *args, **kwargs):
        # Sample menu items by cuisine
        menu_items = {
            'Italian': [
                ('Margherita Pizza', 'Classic tomato sauce, fresh mozzarella, basil', 14.99),
                ('Spaghetti Carbonara', 'Eggs, pecorino cheese, pancetta, black pepper', 16.99),
                ('Lasagna', 'Layered pasta with meat sauce and cheese', 18.99),
                ('Tiramisu', 'Coffee-flavored Italian dessert', 8.99),
                ('Bruschetta', 'Grilled bread with tomatoes, garlic, and basil', 7.99)
            ],
            'Chinese': [
                ('Kung Pao Chicken', 'Spicy diced chicken with peanuts and vegetables', 15.99),
                ('Dim Sum Platter', 'Assorted steamed dumplings', 12.99),
                ('Mapo Tofu', 'Spicy tofu with minced pork', 13.99),
                ('Spring Rolls', 'Crispy rolls with vegetables', 6.99),
                ('Fried Rice', 'Wok-fried rice with eggs and vegetables', 11.99)
            ],
            'Indian': [
                ('Butter Chicken', 'Creamy tomato curry with tender chicken', 16.99),
                ('Vegetable Biryani', 'Fragrant rice with mixed vegetables', 14.99),
                ('Naan Bread', 'Traditional Indian flatbread', 3.99),
                ('Palak Paneer', 'Spinach curry with cheese', 13.99),
                ('Samosas', 'Crispy pastries with spiced potatoes', 5.99)
            ],
            'Mexican': [
                ('Tacos al Pastor', 'Marinated pork tacos with pineapple', 12.99),
                ('Guacamole', 'Fresh avocado dip with chips', 8.99),
                ('Enchiladas', 'Rolled tortillas with chicken and sauce', 14.99),
                ('Quesadillas', 'Grilled tortillas with cheese and fillings', 11.99),
                ('Churros', 'Mexican fried dough with cinnamon sugar', 6.99)
            ],
            'Japanese': [
                ('Sushi Combo', 'Assorted fresh sushi rolls', 22.99),
                ('Ramen', 'Noodle soup with pork and egg', 15.99),
                ('Tempura', 'Crispy battered shrimp and vegetables', 16.99),
                ('Miso Soup', 'Traditional Japanese soup', 4.99),
                ('Teriyaki Chicken', 'Grilled chicken with teriyaki sauce', 17.99)
            ],
            'Thai': [
                ('Pad Thai', 'Stir-fried rice noodles with shrimp', 14.99),
                ('Green Curry', 'Coconut curry with chicken', 15.99),
                ('Tom Yum Soup', 'Spicy and sour soup', 7.99),
                ('Spring Rolls', 'Fresh rolls with peanut sauce', 6.99),
                ('Mango Sticky Rice', 'Sweet coconut rice with fresh mango', 8.99)
            ],
            'French': [
                ('Coq au Vin', 'Braised chicken in wine sauce', 24.99),
                ('French Onion Soup', 'Classic onion soup with cheese', 9.99),
                ('Beef Bourguignon', 'Beef stew in red wine', 26.99),
                ('Crème Brûlée', 'Classic French custard dessert', 8.99),
                ('Escargot', 'Snails in garlic herb butter', 12.99)
            ],
            'Mediterranean': [
                ('Greek Salad', 'Fresh vegetables with feta cheese', 11.99),
                ('Hummus Plate', 'Chickpea dip with pita bread', 8.99),
                ('Falafel Plate', 'Fried chickpea patties with tahini', 13.99),
                ('Moussaka', 'Layered eggplant and meat casserole', 16.99),
                ('Baklava', 'Sweet pastry with nuts and honey', 7.99)
            ],
            'American': [
                ('Classic Burger', 'Beef patty with lettuce and tomato', 13.99),
                ('Mac and Cheese', 'Creamy cheese pasta', 12.99),
                ('BBQ Ribs', 'Slow-cooked pork ribs', 22.99),
                ('Caesar Salad', 'Romaine lettuce with Caesar dressing', 10.99),
                ('Apple Pie', 'Traditional American dessert', 6.99)
            ],
            'Korean': [
                ('Bulgogi', 'Marinated beef with rice', 17.99),
                ('Kimchi Stew', 'Spicy fermented cabbage stew', 14.99),
                ('Bibimbap', 'Mixed rice with vegetables and egg', 15.99),
                ('Korean Fried Chicken', 'Crispy chicken with spicy sauce', 16.99),
                ('Tteokbokki', 'Spicy rice cakes', 11.99)
            ]
        }

        # Process each business
        businesses = Business.objects.all()
        for business in businesses:
            try:
                # Get cuisine
                cuisine_obj = business.cuisine.first()
                if cuisine_obj and cuisine_obj.cuisine_name in menu_items:
                    # Create menu items for this restaurant
                    for item in menu_items[cuisine_obj.cuisine_name]:
                        name, description, price = item
                        
                        # Check if dish already exists for this business
                        if not Dish.objects.filter(
                            dish_name=name,
                            business_id=business
                        ).exists():
                            # Create the dish
                            dish = Dish.objects.create(
                                business_id=business,
                                cuisine_id=cuisine_obj,  # Add the cuisine
                                dish_name=name,
                                dish_description=description,
                                dish_cost=price,
                                dish_type_id =1
                            )
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Created dish "{name}" for {business.business_name}'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Dish "{name}" already exists for {business.business_name}'
                                )
                            )
                            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error creating menu for {business.business_name}: {str(e)}'
                    )
                )

        self.stdout.write(self.style.SUCCESS('Finished creating sample menus'))