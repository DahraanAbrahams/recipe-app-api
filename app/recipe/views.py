"""Views for the Recipe APIs"""

from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all() #queryset represents the objs that are available for this viewset. Because its a ModelViewset, 
                                    #its expected to work with a model. The way we tell it what model to use is, you sepcify the queryset
                                    #i.e. this is the queryset of objs that is going to be manageable through this API, or the APIs through our ModelViewset  
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # We're overriding the default get method because we only want to get the authenticated users recipes 
        """Retrieve recipes for authenticated user"""
        return self.queryset.filter(user = self.request.user).order_by('-id')
    
