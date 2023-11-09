'''
Database models for the API
'''
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, \
    BaseUserManager, PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):
    '''
    Manager for the custom user model
    '''
    def create_user(self, email, password=None, **extra_fields):
        '''
        Creates and saves a new user
        '''
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        # set_password() is a Django helper function that hashes the password
        user.set_password(password)
        user.save(using=self._db)  # Support multiple databases
        return user

    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    '''
    Custom user model that supports using email instead of username
    '''
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    # Required for all Django models
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()  # Assign the UserManager to the objects attribute

    USERNAME_FIELD = 'email'


class Destination(models.Model):
    '''
    Destination object
    '''
    # user field is a foreign key to the user model
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        # If the user is deleted, delete the destination
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=2, decimal_places=1)

    def __str__(self):
        return self.name
