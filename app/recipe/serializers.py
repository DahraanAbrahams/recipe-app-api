"""Serializers for recipe APIs"""

from rest_framework import serializers
from core.models import (
   Recipe,
   Tag,
   Ingredient
)

class IngredientSerializer(serializers.ModelSerializer):
   """Serializer for ingredients"""

   class Meta:
      model = Ingredient
      fields = ['id', 'name']
      read_only_fields = ['id']

class TagSerializer(serializers.ModelSerializer):
   """Serializer for tags"""

   class Meta:
      model = Tag
      fields = ['id', 'name']
      read_only_fields = ['id']


class RecipeSerializer(serializers.ModelSerializer): #We're using the ModelSerializer because this serializer is going to represent a spcific model in the system - Recipe Model
   """Serializer for recipes"""

   tags = TagSerializer(many=True, required=False)
   ingredients = IngredientSerializer(many=True, required=False)

   class Meta:
      model = Recipe
      fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags', 
                'ingredient']
      read_only_fields = ['id']

   def _get_or_create_tags(self, tags, recipe):
      """Handle getting or creating tags as needed"""
      auth_user = self.context['request'].user #Because we're getting auth_user in a serializer and not the view, we use context
      #Context is passed to the serializer by the view when you're using the serializer for a particular view
      for tag in tags:
         tag_obj, created = Tag.objects.get_or_create(#get_or_create is a helper method available for your model manager
            #It gets the value if it already exists or it creates the value with the passed in values if it doesn't exist
            user = auth_user,
            **tag,
         )
         recipe.tags.add(tag_obj)

   def _get_or_create_ingredients(self, ingredients, recipe): #_method is used internally only "private", i.e. we don't expect
      #anyone using this serializer to be calling _get_or_create_ingredients directly. It should only be used by other 
      #methods inside the RecipeSerializer. There's no technical restriction on it however it's best practice not too
      """Handle getting or creating ingredients as needed"""

      auth_user = self.context['request'].user
      for ingredient in ingredients:
         ingredient_obj, create = Ingredient.objects.get_or_create( #gets obj if exists or create new
            #gives a 'create' attr - boolean to know whether the ingredient_obj was created or not. We don't need to us it  
            user = auth_user,
            **ingredient
         )
         recipe.ingredients.add(ingredient_obj)

   def create(self, validated_data):
      """Create a recipe"""
      tags = validated_data.pop('tags', []) #removing tags
      ingredients = validated_data.pop('ingredients', []) #removing ingredients
      recipe = Recipe.objects.create(**validated_data) #creating a recipe with excluded tags
      
      self._get_or_create_tags(tags, recipe)
      self._get_or_create_tags(ingredients, recipe)

      return recipe
   
   def update(self, instance, validated_data):
      """Update recipe"""

      tags = validated_data.pop('tags', None)
      if tags is not None:
         instance.tags.clear()
         self._get_or_create_tags(tags, instance)

      for attr, value in validated_data.items():
         setattr(instance, attr, value)

      instance.save()
      return instance



class RecipeDetailSerializer(RecipeSerializer):#DetailSerializer is going to be an extension of the RecipeSerializer
   """Serializer for the recipe detail view"""
   #We will just add extra fields to the RecipeSerializer which avoids us having to create a new Model etc for the DetailSerializer
   
   class Meta(RecipeSerializer.Meta):
      fields = RecipeSerializer.Meta.fields + ['description']
