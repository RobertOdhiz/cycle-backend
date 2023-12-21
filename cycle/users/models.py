from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from uuid import uuid4
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    UserManager class that inherits from the BaseUserManager
    """
    def create_user(self, email, username, first_name, password, **other_fields):
        """
        Base function responsible for creating each user instance
        """

        other_fields.setdefault('is_active', True)

        if not email:
            raise ValueError("Please enter an email address")
        
        email = self.normalize_email(email)
        if not username:
            username, domain = email.split('@')
        user = self.model(email=email, username=username, first_name=first_name, **other_fields)

        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, username, first_name, password, **other_fields):
        """
        Function that handles creation of a superuser instance
        """
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('role', 'ADMIN')

        if other_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff set to True")
        
        if other_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser set to True")
        
        return self.create_user(email, first_name, username, password, **other_fields)


        

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True, null=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        RENTER = "RENTER", "Renter"
        RENTEE = "RENTEE", "Rentee"

    base_role = Role.ADMIN

    role = models.CharField(max_length=50, choices=Role.choices)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'username']

    def has_permission(self, request, view):
        if view.action == 'list' and not self.is_superuser:
            return False
        if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return str(request.user.id) == view.kwargs['pk']
        return True

    def __str__(self):
        return self.first_name + self.last_name
    
    # def natural_key(self):
    #     return (self.username,)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
            return super().save(*args, **kwargs)


class RenterManager(BaseUserManager):

    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.RENTER)


class Renter(User):
    base_role = User.Role.RENTER
    renter = RenterManager()

    institution = models.CharField(max_length=255, blank=False)
    phone_number = models.CharField(max_length=10, blank=False)
    registration_number = models.CharField(max_length=255, blank=False)

    class Meta:
        proxy = False

class Rent(models.Model):
    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    rental_date = models.DateField()


class RenterProfile(models.Model):
    user = models.OneToOneField(Renter, on_delete=models.CASCADE)
    renter_id = models.CharField(max_length=60, unique=True)
    last_rent_date = models.DateField(null=True, blank=True)
    max_rent_streak = models.IntegerField(default=0)

    def __str__(self):
        return self.user.first_name


@receiver(post_save, sender=Renter)
def create_renter_profile(sender, instance, created, **kwargs):
    """ FUnction based receiver view that creates a renter profile automatically the renter is created """
    if created and instance.role == "RENTER":
        RenterProfile.objects.create(user=instance, renter_id=uuid4(), max_rent_streak=0)

@receiver(post_save, sender=Rent)
def update_rent_streak_on_rent(sender, instance, created, **kwargs):
    """ Receiver function that updates  the rent streaks on the renter profile """
    if created and instance.role == 'RENTER':
        renter_profile = RenterProfile.objects.get(user=instance.renter)
        update_rent_streak(renter_profile)


class RenteeManager(BaseUserManager):
    """ rentee Manager that handles database queries for all Rentee users """
    def get_queryset(self, *args, **kwargs):
        """ Filters the results based on Rentee Role """
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.RENTEE)


class Rentee(User):
    """ Rentee class that handles Creation of all Rentee instance objects """
    # Setting the base role appropriately
    base_role = User.Role.RENTEE

    Rentee = RenteeManager()

    class Meta:
        proxy = True


class RenteeProfile(models.Model):
    """ Handles Creation of Rentee-Profile objects """
    user = models.OneToOneField(Rentee, on_delete=models.CASCADE)
    rentee_id = models.CharField(max_length=60, unique=True)

    def __str__(self):
        return self.rentee_id


@receiver(post_save, sender=Rentee)
def create_rentee_profile(sender, instance, created, **kwargs):
    """ receiver function for creating rentee profile when a new Rentee object is created """
    if created and instance.role == "RENTEE":
        RenteeProfile.objects.create(user=instance, rentee_id=uuid4())


def update_rent_streak(renter_profile):
    """ Handles updating the renter's rent streak """
    today = renter_profile.last_rent_date

    if not today or today != renter_profile.last_rent_date:
        renter_profile.max_rent_streak = 1
    else:
        yesterday = today - timedelta(days=1)
        if yesterday == renter_profile.last_rent_date:
            renter_profile.max_rent_streak += 1
        else:
            renter_profile.max_rent_streak = 1


class AdminManager(BaseUserManager):
    """ Handles database queries for all admin instances """
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.ADMIN)
    
class Administrator(User):
    """Administrator class that handles creation of app admins """
    base_role = User.Role.ADMIN

    admin = AdminManager()

    id = uuid4()
    joined_on = models.DateTimeField(default=timezone.now)