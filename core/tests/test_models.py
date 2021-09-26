from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email='test@test.com', password='testpass'):
    """ Create user for testing """
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        """ Test creating a new user with email correctly """

        email = 'test@test.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test normalized email for a new user """

        email = 'test@TEST.COM'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ New invalid user email """

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')
    
    def test_create_new_superuser(self):
        """ Test creation of a super user """

        email = 'test@test.com'
        password = 'test123'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_tag_str(self):
        """ Test representation in str of the tag """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Meat'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """ Test representation in str of the ingredient """
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Banana'
        )

        self.assertEqual(str(ingredient), ingredient.name)
    
    def test_recipe_str(self):
        """ Test representation in str of the recipes """
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and Mushroom sauce',
            time_minutes=5,
            price=5.00
        )

        self.assertEqual(str(recipe), recipe.title)


