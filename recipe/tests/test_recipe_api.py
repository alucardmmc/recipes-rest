from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')

def sample_tag(user, name='Main Course'):
    """ Create Example Tag """
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinnamon'):
    """ Create Example Ingredient """
    return Ingredient.objects.create(user=user, name=name)

def detail_url(recipe_id):
    """ Return Recipe Detail URL """
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_recipe(user, **params):
    """ Create and return a recipe """
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 10,
        'price': 5.00,
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)

class PrivateRecipeAPITests(TestCase):
    """ Test with Authenticated access to API """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'test123',
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_recipes(self):
        """ Test get list of recipes """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """ Test get recipes by user """
        user2 = get_user_model().objects.create_user(
            'another@test.com',
            'test123',
        )

        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
    
    def test_view_recipe_detail(self):
        """ Test view the details of a recipe """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
    
    def test_create_basic_recipe(self):
        """ Test create recipe without ingredients nor tags """
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 30,
            'price': 10.00,
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))
    
    def test_create_recipe_with_tags(self):
        """ Test create recipe with tags """
        tag1 = sample_tag(user=self.user, name='Tag 1')
        tag2 = sample_tag(user=self.user, name='Tag 2')
        payload = {
            'title': 'Test recipe with two tags',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 10.00,
        }
        
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """ Test create recipe with ingredients """
        ingredient1 = sample_ingredient(user=self.user, name='Ingredient 1')
        ingredient2 = sample_ingredient(user=self.user, name='Ingredient 2')
        payload = {
            'title': 'Test recipe with ingredients',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 45,
            'price': 15.00,
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)



# class PrivateRecipeAPITests(TestCase):
#     """ Testi With Authenticated access to API """







