"""
Database models
"""
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

#User Model Manager
class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """Create, Save, Return a new user"""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db) #using=self._db is just to support adding multiple DBs - Best Practice for incase you have multiple DBs

        return user

    def create_superuser(self, email, password):
        """Create and Return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user




class User(AbstractBaseUser, PermissionsMixin):
    #AbstractBaseUser contains functionality for auth system but not any fields. 
    #PermissionsMixin contains functionality for the permissions and fields
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager() #Creates instance of Manager - this is how you assign a user manager in Django

    USERNAME_FIELD = 'email' #Defines field that we want to use for authentication. This is how we replace the username
                             #default field that comes with the default user model to our custom email field
    
class Recipe(models.Model):
    """Recipe Object"""
    user = models.ForeignKey(   #Used to store the user that the recipe belongs to. The ForeignKey allows us to setup a relationship between the recipe model and another model
        settings.AUTH_USER_MODEL, #That relationship TO is the AUTH_USER_MODEL which we defined in our settings.py file (User Model)
        on_delete = models.CASCADE, #If the related object gets deleted, we cascade that i.e. if the user is deleted, we also delete all recipes associated with that user
    )

    title = models.CharField(max_length = 255)
    description = models.TextField(blank = True) #Holds more content than a Charfield and could have multiple different lines of content
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank = True)

    def __str__(self):
        return self.title