"""Views for the Recipe APIs"""

from rest_framework import (
    viewsets, 
    mixins #Things you can mix-in to a view to add extra functionality
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe, 
    Tag
)
from recipe import serializers

class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs"""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all() #queryset represents the objs that are available for this viewset. Because its a ModelViewset, 
                                    #its expected to work with a model. The way we tell it what model to use is, you sepcify the queryset
                                    #i.e. this is the queryset of objs that is going to be manageable through this API, or the APIs through our ModelViewset  
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # We're overriding the default get method because we only want to get the authenticated users recipes 
        """Retrieve recipes for authenticated user"""
        return self.queryset.filter(user = self.request.user).order_by('-id')
    
    def get_serializer_class(self): #Overriding default get_serializer_class to return the serilizer based on endpoint
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.RecipeSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):#perform_create method is the way we override the behaviour for when DRF saves a model in a Viewset
        #Essentially, when we perform a creation of a new obj through this Model Viewset, i.e. when we create a new recipe through the
        #create feature of the Viewset, we're going to call this method as part of that obj creation. It accepts 1 param, serializer
        #which is the validated serializer
        """Create new recipe"""
        serializer.save(user=self.request.user) #Will set the user value to the current authenticated user when we save the obj
    
class TagViewSet(mixins.UpdateModelMixin, 
                 mixins.DestroyModelMixin, 
                 mixins.ListModelMixin, 
                 viewsets.GenericViewSet):
    #mixins.ListModelMixin -> Allows you to add the list functionality for listing models
    #viewsets.GenericViewSet -> Allows us to add in mixins so tha we can have the viewset fucntionality that we desire for your API
    """Manage tags in the DB"""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self): # We're overriding the default get method because we only want to get the authenticated users recipes 
        """Filter queryset to authenticated user"""
        return self.queryset.filter(user = self.request.user).order_by('-name')