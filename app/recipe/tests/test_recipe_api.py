"""Tests for recipe APIs"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')

def create_recipe(user, **params): #params will be a dictionary with all the values passed to the test which we then upack and override
    """Create and return a sample recipe"""
    defaults = {    #We create this helper function/block of default values so because for our tests, we won't necessailry provide all values
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
        'link': 'http://example.com/recipe.pdf',
    } #But still allows us to override these values if we need to
    #Because params is a dictionary, we don't want to transform the values because it may have unexpected results. If you modify
    #dictionary arguments, then it could reflect the argumnents that are passed into the function, so we create a new dictionary 'defaults' 
    defaults.update(params) # then we call update which updates defaults with any VALUES that were passed in params

    recipe = Recipe.objects.create(user = user, **defaults)
    return recipe

class PublicRecipeAPITests(TestCase): #This test class, tests the Public API, so it tests as an unauthenticated user
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient() #This gives us a test client that we can use for the tests added to this class

    def test_auth_required(self): #This simply checks that authentication is required for getting recipes 
        """Test auth is required """ 
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.client = APIClient() #Creates a client
        self.user = get_user_model().objects.create_user( #Creates a user
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)#Authenticates the client with that user

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        create_recipe(user = self.user) #recipe = Recipe.objects.create(user = user, **defaults) -> user is the only required param for create_recipe helper function 
        create_recipe(user = self.user)

        res = self.client.get(RECIPES_URL) #response to API performing get request

        recipes = Recipe.objects.all().order_by('-id') # We are returning the recipes in reverse order
        serializer = RecipeSerializer(recipes, many=True) # We using serializer in our tests because this is how we are going to compare the expected response from the API
        #NB: Serializers can either return a detail which is one item, or a list of items -> many=True says we want to pass in a list of items
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data) #res.data -> data dictionary returned from the response
                                                    #serializer.data -> data dictionary of the objs passed through serializer
        
    def test_recipes_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user"""

        other_user = get_user_model().objects.create_user( #Creates another user
            'other@example.com',
            'password123',
        )

        create_recipe(user = other_user) #recipe = Recipe.objects.create(user = user, **defaults) -> user is the only required param for create_recipe helper function 
        create_recipe(user = self.user)

        res = self.client.get(RECIPES_URL) #response to API performing get request

        recipes = Recipe.objects.filter(user = self.user)
        serializer = RecipeSerializer(recipes, many=True) 
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data) #res.data -> data dictionary returned from the response
                                                    #serializer.data -> data dictionary of the objs passed through serializer