from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from Restaurant_handling.models import (
    DieteryPreference, 
    Cuisine, 
    DishType, 
    Dish, 
    Review
)
from gfgauth.models import Business

class DieteryPreferenceTests(TestCase):
    def setUp(self):
        self.dietary_pref = DieteryPreference.objects.create(
            dietery_name='  Vegetarian  '  # Added spaces to test strip()
        )

    def test_dietary_preference_str(self):
        """Test the string representation of dietary preference"""
        self.assertEqual(str(self.dietary_pref), 'Vegetarian')

    def test_dietary_preference_name_max_length(self):
        """Test that dietary preference name respects max length"""
        max_length = self.dietary_pref._meta.get_field('dietery_name').max_length
        self.assertEqual(max_length, 100)

class CuisineTests(TestCase):
    def setUp(self):
        self.cuisine = Cuisine.objects.create(
            cuisine_name='Italian'
        )

    def test_cuisine_str(self):
        """Test the string representation of cuisine"""
        self.assertEqual(str(self.cuisine), 'Italian')

    def test_cuisine_name_max_length(self):
        """Test that cuisine name respects max length"""
        max_length = self.cuisine._meta.get_field('cuisine_name').max_length
        self.assertEqual(max_length, 100)

class DishTypeTests(TestCase):
    def setUp(self):
        self.dish_type = DishType.objects.create(
            dish_type_name='Main Course'
        )

    def test_dish_type_str(self):
        """Test the string representation of dish type"""
        self.assertEqual(str(self.dish_type), 'Main Course')

    def test_dish_type_name_max_length(self):
        """Test that dish type name respects max length"""
        max_length = self.dish_type._meta.get_field('dish_type_name').max_length
        self.assertEqual(max_length, 100)

class DishTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create business with correct fields
        self.business = Business.objects.create(
            business_owner=self.user,
            business_name='Test Restaurant',
            business_address='123 Test St',
            business_tax_code='TEST123',
            business_max_table_capacity=4,
            contact_number='1234567890',
            business_description='Test restaurant description'
        )
        
        self.cuisine = Cuisine.objects.create(cuisine_name='Italian')
        self.dish_type = DishType.objects.create(dish_type_name='Main Course')
        self.dietary_pref = DieteryPreference.objects.create(dietery_name='Vegetarian')
        
        self.dish = Dish.objects.create(
            dish_name='Margherita Pizza',
            dish_cost=Decimal('12.99'),
            dish_type=self.dish_type,
            cuisine_id=self.cuisine,
            business_id=self.business,
            dish_description='Classic Italian pizza',
            is_available=True
        )
        self.dish.allergens.add(self.dietary_pref)

    def test_dish_str(self):
        """Test the string representation of dish"""
        self.assertEqual(str(self.dish), 'Margherita Pizza')

    def test_dish_fields_max_length(self):
        """Test that dish fields respect max length"""
        name_max_length = self.dish._meta.get_field('dish_name').max_length
        desc_max_length = self.dish._meta.get_field('dish_description').max_length
        self.assertEqual(name_max_length, 100)
        self.assertEqual(desc_max_length, 100)

    def test_dish_cost_decimal_places(self):
        """Test that dish cost field handles decimal places correctly"""
        self.assertEqual(self.dish.dish_cost, Decimal('12.99'))
        max_digits = self.dish._meta.get_field('dish_cost').max_digits
        decimal_places = self.dish._meta.get_field('dish_cost').decimal_places
        self.assertEqual(max_digits, 10)
        self.assertEqual(decimal_places, 2)

    def test_dish_allergens(self):
        """Test the many-to-many relationship with allergens"""
        self.assertEqual(self.dish.allergens.count(), 1)
        self.assertEqual(self.dish.get_allergens_display(), 'Vegetarian')

    def test_dish_availability_default(self):
        """Test the default value of is_available field"""
        new_dish = Dish.objects.create(
            dish_name='Test Dish',
            dish_cost=Decimal('10.00'),
            dish_type=self.dish_type,
            cuisine_id=self.cuisine,
            business_id=self.business,
            dish_description='Test description'
        )
        self.assertTrue(new_dish.is_available)

class ReviewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create business with correct fields
        self.business = Business.objects.create(
            business_owner=self.user,
            business_name='Test Restaurant',
            business_address='123 Test St',
            business_tax_code='TEST123',
            business_max_table_capacity=4,
            contact_number='1234567890',
            business_description='Test restaurant description'
        )
        
        self.review = Review.objects.create(
            review_rating=5,
            review_text='Excellent food and service!',
            business_id=self.business,
            user_id=self.user
        )

    def test_review_str(self):
        """Test the string representation of review"""
        self.assertEqual(str(self.review), str(self.review.review_id))

    def test_review_text_max_length(self):
        """Test that review text respects max length"""
        max_length = self.review._meta.get_field('review_text').max_length
        self.assertEqual(max_length, 100)

    def test_review_rating_constraints(self):
        """Test that review rating is an integer"""
        self.assertEqual(type(self.review.review_rating), int)

    def test_review_relationships(self):
        """Test the relationships with Business and CustomUser"""
        self.assertEqual(self.review.business_id, self.business)
        self.assertEqual(self.review.user_id, self.user)