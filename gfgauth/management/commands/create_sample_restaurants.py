# gfgauth/management/commands/create_sample_restaurants.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from gfgauth.models import Business
from Restaurant_handling.models import Cuisine
import random
from datetime import time

class Command(BaseCommand):
    help = 'Creates 10 sample restaurant profiles'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        # Create Business group if it doesn't exist
        business_group, _ = Group.objects.get_or_create(name='Business')
        
        # Sample data
        cuisines = [
            'Italian', 'Chinese', 'Indian', 'Mexican', 'Japanese',
            'Thai', 'French', 'Mediterranean', 'American', 'Korean'
        ]
        
        # Create cuisines if they don't exist
        cuisine_objects = []
        for cuisine_name in cuisines:
            cuisine, created = Cuisine.objects.get_or_create(cuisine_name=cuisine_name)  # Changed from name to cuisine_name
            cuisine_objects.append(cuisine)
        
        restaurant_names = [
            "The Hungry Fork", "Golden Dragon", "Spice Route",
            "Casa Mexicana", "Sakura Sushi", "Thai Orchid",
            "Le Petit Bistro", "Mediterranean Delight",
            "American Diner", "Seoul Kitchen"
        ]
        
        addresses = [
            "123 Main St, New York, NY", 
            "456 Oak Ave, Los Angeles, CA", 
            "789 Maple Rd, Chicago, IL",
            "321 Pine Ln, Houston, TX", 
            "654 Cedar Blvd, Phoenix, AZ", 
            "987 Elm St, Philadelphia, PA",
            "147 Birch Dr, San Antonio, TX", 
            "258 Willow Way, San Diego, CA", 
            "369 Cherry Lane, Dallas, TX",
            "741 Spruce Court, San Jose, CA"
        ]

        for i in range(10):
            try:
                # Create user
                username = f"restaurant_owner_{i+1}"
                email = f"restaurant{i+1}@example.com"
                password = "testpass123"
                
                # Check if user already exists
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=f"Owner{i+1}",
                        last_name=f"Family{i+1}"
                    )
                    # Add user to Business group
                    user.groups.add(business_group)
                else:
                    user = User.objects.get(username=username)

                # Check if business already exists
                if not Business.objects.filter(business_name=restaurant_names[i]).exists():
                    # Generate random time for opening/closing
                    opening_time = time(random.randint(6, 11), 0)  # 6 AM to 11 AM
                    closing_time = time(random.randint(18, 23), 0)  # 6 PM to 11 PM
                    
                    # Create business profile
                    business = Business.objects.create(
                        business_name=restaurant_names[i],
                        business_owner=user,
                        business_address=addresses[i],
                        business_tax_code=f"TAX{i+1}2024",
                        contact_number=f"+1-555-{i:03d}-{random.randint(1000,9999)}",
                        opening_time=opening_time,
                        closing_time=closing_time,
                    )
                    
                    # Add cuisine
                    business.cuisine.add(cuisine_objects[i])
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created restaurant: {business.business_name}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Restaurant {restaurant_names[i]} already exists'
                        )
                    )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error creating restaurant {i+1}: {str(e)}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS('Finished creating sample restaurants')
        )