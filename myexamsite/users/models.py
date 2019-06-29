from django.db import models

# Create your models here.
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from datetime import datetime
from django.core.validators import RegexValidator




class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
class User(AbstractBaseUser,PermissionsMixin):
	gender_choices = (
        ('male','Male'),
        ('female','Female'),
        ('others','Others'),
        )
	email = models.EmailField(verbose_name='email address',max_length=255,unique=True,)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	gender = models.CharField(max_length=5,choices=gender_choices,default='male')
	phone_regex = RegexValidator(regex=r'^(0|91)?[789][0-9]{9}$', message="Enter valid phone number")
	mobile = models.CharField(max_length=13,validators=[phone_regex])
	date_of_birth = models.DateField(blank=True,null=True)
	date_joined = models.DateTimeField('date joined',default=datetime.now)
	is_active=models.BooleanField(default=True)
	is_staff=models.BooleanField(default=False)
	is_admin=models.BooleanField(default=False)
	username=models.CharField(max_length=255,blank=True,null=True)
	objects=UserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	def __str__(self):
		return self.first_name+" "+self.last_name




