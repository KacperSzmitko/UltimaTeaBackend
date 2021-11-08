from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class Machine(models.Model):
    machine_id =  models.CharField(primary_key=True, max_length=32)
    brewing_temperature =  models.FloatField(default=0, null=True)
    air_temperature =  models.FloatField(default=0, null=True)
    mug_temperature =  models.FloatField(default=0, null=True)
    water_container_weight =  models.FloatField(default=0, null=True)
    first_container_weight =  models.FloatField(default=0, null=True)
    second_container_weight =  models.FloatField(default=0, null=True)
    third_container_weight =  models.FloatField(default=0, null=True)
    is_mug_ready =  models.BooleanField(default=False, null=True)
    is_user_active =  models.BooleanField(default=False, null=True)
    state_of_the_tea_making_process =  models.IntegerField(default=0, null=True)

    class Meta:
        db_table = "machine"

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email"), unique=True)
    machine = models.ForeignKey(Machine, null=True, blank=False, on_delete=models.SET_NULL)
    image = models.ImageField(height_field=150, width_field=150)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email



