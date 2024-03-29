"""URL mappings for the recipe app"""

from django.urls import (
    path, include,
)

from rest_framework.routers import DefaultRouter #can be used with an APIView to automatically create routes for all of the different options available for that view 

from recipe import views

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)# This will create a new endpoint -> api/recipes and it will assign all of the different endpoints from our recipe viewset to that endpoint 
#The recipe viewset is going to have autogenerated URLs depending on the functionality that's enabled on the viewset
#Because we are using the ModelViewSet, it's going to support all the available methods to create, read, update and delete
#IT will create a register endpoints for eahc of those options
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

app_name = 'recipe' #We define the name that is used to identify the name when we do the reverse lookup of URLs

urlpatterns = [
    path('', include(router.urls)), #include the URLs that are automatically generated by the router
]