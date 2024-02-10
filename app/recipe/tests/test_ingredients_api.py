"""Tests for the ingredients API"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient
)
from recipe.serializers import (
    IngredientSerializer,
)

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_user(email='user@example.com', password='password123'): #Helper function to help create users in the system
    """Create and return new user"""
    return get_user_model().objects.create_user(email=email, password=password)

def detail_url(ingredient_id):#This is for specifying a specific recipe to see its details
    """Create and return a ingredient details URL"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])# We can now use this to generate a unique URL for a specific recipes detail endpoint


class PublicRecipeAPITests(TestCase): #This test class, tests the Public API, so it tests as an unauthenticated user
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient() #This gives us a test client that we can use for the tests added to this class

    def test_auth_required(self): #This simply checks that authentication is required for getting recipes 
        """Test auth is required for returning ingredients""" 
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient() #Creates a client
        self.client.force_authenticate(self.user)#Authenticates the client with that user

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients"""

        Ingredient.objects.create(user=self.user, name='kale')
        Ingredient.objects.create(user=self.user, name='vanilla')

        res = self.client.get(INGREDIENTS_URL)

        #NB: DB is entirely refreshed for every test that is run. The only things that will exist in the DB is 
        #everything we created in setUp()

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to authenticated user"""

        user2 = create_user(email = 'other@example.com')

        Ingredient.objects.create(user=user2, name='salt')
        ingredient = Ingredient.objects.create(user=self.user, name='pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1) 
        self.assertEqual(res.data[0]['name'], ingredient.name) 
        self.assertEqual(res.data[0]['id'], ingredient.id) 

    
    def test_update_ingredient(self):
        """Test updating an ingredient"""

        ingredient = Ingredient.objects.create(user = self.user, name='cilantro')

        payload = {'name': 'coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleteing an ingredient"""

        ingredient = Ingredient.objects.create(user=self.user, name='lettuce')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())


