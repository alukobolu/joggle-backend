from django.db import models
import secrets
import uuid
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
# from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta


#This is the folder where profile images are stored
def upload_location(instance, filename):
	file_path = 'profile_image/{user_id}/{image}'.format(user_id=str(instance.id), image=filename)
	return file_path


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):

    username = None
    email = models.EmailField(unique=True,
                              max_length=255,
                              blank=False)

    verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class UserAccount(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=CASCADE)
    firstname = models.CharField(max_length=200, null=True, blank=True)
    lastname = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    profile_image = models.FileField(null=True, blank=True)
    deactivated = models.BooleanField(default=False)
    is_loggedin	= models.BooleanField(default=False)
    expo_token = models.CharField(max_length=50000, null=True, blank=True)   
    is_blocked = models.BooleanField(default=False)                 

    def __str__(self):
        return self.user.email

    def fullname(self):
        return f"{self.firstname} {self.lastname}"
    # For checking permissions. to keep it simple all admin have ALL permissons
    def has_perm(self, perm, obj=None):
        return self.is_admin

    # Does this user have permission to view this app? (ALWAYS YES FOR SIMPLICITY)
    def has_module_perms(self, app_label):
        return True
    
class UserOtp(models.Model) : 
    code = models.CharField(max_length=250, null=True,blank = True)
    email = models.CharField(max_length=250, null=True,blank = True)
    expire_at = models.DateTimeField(blank = True)
    created_at = models.DateTimeField(auto_now_add=True, blank = True)

    def __str__(self):
        return self.email

class UserDevices(models.Model) : 
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    expo_token = models.CharField(max_length=50000, null=True, blank=True)   
    device          =       models.CharField(max_length=150,null=True, blank=True)
    device_os       =       models.CharField(max_length=150,null=True, blank=True)
    page_visited    =       models.CharField(max_length=150,null=True, blank=True)
    user_city       =       models.CharField(max_length=150,null=True, blank=True)
    user_country    =       models.CharField(max_length=150,null=True, blank=True)
    user_browser    =       models.CharField(max_length=150,null=True, blank=True)
    Ip_address      =       models.CharField(max_length=150,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank = True)

    def __str__(self):
        return self.user.email




def now_plus_year():
    return datetime.now() - timedelta(days=365)
