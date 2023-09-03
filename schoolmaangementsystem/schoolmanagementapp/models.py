from django.db import models

from django.db import models
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.models import User


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserCredentialsManager(BaseUserManager):
    def create_user(self, email, role, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, role, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, role, password, **extra_fields)

class UserCredentials(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('principal', 'Principal'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField(Group, related_name="usercredentials_set", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, 
        related_name="usercredentials_set",
        blank=True
    )
    objects = UserCredentialsManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return self.email
    

class Principal(models.Model):
    user = models.ForeignKey(UserCredentials, on_delete=models.CASCADE,null=True)
    email = models.EmailField(unique=True)
    username=models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_created = models.DateTimeField(auto_now=True)



class Teacher(models.Model):
    user = models.ForeignKey(UserCredentials, on_delete=models.CASCADE,null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_joined = models.DateField(auto_now=True)
    subjects = models.ManyToManyField('Subject')

    def __str__(self):
        return self.first_name 
   

class Student(models.Model):
    user = models.ForeignKey(UserCredentials, on_delete=models.CASCADE,null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_joined = models.DateField(auto_now_add=True)
    class_room = models.ForeignKey('ClassRoom', on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.first_name  

class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class ClassRoom(models.Model):
    name = models.CharField(max_length=100)
    grade = models.PositiveIntegerField()
    teacher = models.OneToOneField(Teacher, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.name
