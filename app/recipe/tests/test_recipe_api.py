"""Tests for recipe APIs"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Recipe, 
    Tag
)
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):#This is for specifying a specific recipe to see its details
    """Create and return a recipe details URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])# We can now use this to generate a unique URL for a specific recipes detail endpoint


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

def create_user(**params): #Helper function to help create users in the system
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)

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

        self.user = create_user(email = 'user@example.com', password = 'testpass123')
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

        other_user = create_user(email = 'other@example.com', password = 'test123')

        create_recipe(user = other_user) #recipe = Recipe.objects.create(user = user, **defaults) -> user is the only required param for create_recipe helper function 
        create_recipe(user = self.user)

        res = self.client.get(RECIPES_URL) #response to API performing get request

        recipes = Recipe.objects.filter(user = self.user)
        serializer = RecipeSerializer(recipes, many=True) 
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data) #res.data -> data dictionary returned from the response
                                                    #serializer.data -> data dictionary of the objs passed through serializer
        
    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)# Because its a specifc recipe, we don't pass many=True
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe"""
        #We don't want to create a recipe in our test, we want to test if the api is creating a recipe successfully, 
        #so we pass in a payload with contents of a recipe, we want to ensure the recipe was created successfully in the DB
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id = res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of a recipe"""
        #The test is meant to test a partial update. Part of a partial update is ensuring that other fields that aren't presented
        #to the payload aren't updated as part of this change. We wouldn't want to call the partial update and have it remove
        #fields that weren't provided in the fields that needed tp be updated
        original_link = 'https://example.com/recipe.pdf' 
        recipe = create_recipe(
            user = self.user,
            title = 'Sample recipe title',
            link = original_link
        )

        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)#Should only change the title

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()#By default, the model is not refreshed so the values will stil be the same which would in turn fail the test
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe"""
        recipe = create_recipe(
            user = self.user,
            title = 'Sample recipe title',
            link = 'https://example.com/recipe.pdf',
            description = 'Sample recipe description'
        )

        payload = {
            'title': 'New recipe title',
            'link': 'https://example.com/new-recipe.pdf',
            'description': 'New Sample recipe description',
            'time_minutes': 10,
            'price': Decimal('2.50')
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_returns_error(self):
        """Testing changing the recipe user results in error"""
        new_user = create_user(email = 'user2@example.com', password = 'test123')
        recipe = create_recipe(user = self.user)

        payload = {'user': new_user.id}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful"""

        recipe = create_recipe(user = self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error"""

        new_user = create_user(email = 'user2@example.com', password = 'test123')
        recipe = create_recipe(user = new_user)
        url = detail_url(recipe.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Testing creating a recipe with new tags"""

        payload = {
            'title': 'Thai prawn curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json') #format=json necessary for nested serializer

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name = tag['name'],
                user = self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Testing creating a recipe with existing tags"""

        tag_indian = Tag.objects.create(user=self.user, name='Indian')

        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json') #format=json necessary for nested serializer

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name = tag['name'],
                user = self.user,
            ).exists()
            self.assertTrue(exists)


    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe"""

        recipe = create_recipe(user=self.user)
        payload = {'tags': [{'name': 'lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='lunch')
        self.assertIn(new_tag, recipe.tags.all()) #When using many-to-many fields, you don't need to call .refresh_from_db()
        #because essentially, what it's doing under the hood is a new query - recipe.tags.all() is a separate query which will
        #retrieve all of the fresh objects, they aren't cached when you first create the recipe

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""

        tag_breakfast = Tag.objects.create(user=self.user, name='breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='lunch')
        payload = {'tags': [{'name': 'lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipes tags"""

        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)

