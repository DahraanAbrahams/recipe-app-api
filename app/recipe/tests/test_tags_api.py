"""Tests for the tags API"""

from django.contrib.auth import get_user_model
from django.urls import reverse #To figure out URLs that we need to test
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """Create and return a tag details URL"""
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='user@example.com', password = 'testing123'): #Helper function to help create users in the system
    """Create and return new user"""
    return get_user_model().objects.create_user(email=email, password=password)

class PublicTagsApiClient(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient() #This gives us a test client that we can use for the tests added to this class

    def test_auth_required(self): #This simply checks that authentication is required for getting recipes 
        """Test auth is required for retrieving tags""" 
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiClient(TestCase):
    """Test authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient() #Creates a client
        self.client.force_authenticate(self.user)#Authenticates the client with that user

    def test_retrieve_tags(self):
        """Test retrieving a list of tags"""

        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """List of tags is limited to authenticated user"""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Fruity') #tage for another user -> user2. We don't need a ref therefore we don't save in variable. All we need is that it is created in the DB
        tag = Tag.objects.create(user=self.user, name='Comfort food') #tag for authenticated user

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating a tag"""
        tag = Tag.objects.create(user = self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting a tag"""
        tag = Tag.objects.create(user = self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user = self.user)
        self.assertFalse(tags.exists())