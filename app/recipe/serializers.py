"""Serializers for recipe APIs"""

from rest_framework import serializers
from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer): #We're using the ModelSerializer because this serializer is going to represent a spcific model in the system - Recipe Model
   """Serializer for recipes"""

   class Meta:
      model = Recipefields = ['id', 'title', 'time_minutes', 'price', 'link']
      read_only_fields = ['id']