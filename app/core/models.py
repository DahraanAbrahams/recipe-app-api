"""
Database models
"""

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