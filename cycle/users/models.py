from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from uuid import uuid4
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom manager for User model.
    """

    def create_user(self, email, username, first_name, password, **other_fields):
        """
        Creates a regular user.

        Parameters:
        - email: Email address of the user.
        - username: Username of the user.
        - first_name: First name of the user.
        - password: Password for the user.
        - **other_fields: Additional fields for the user model.

        Returns:
        - User instance.
        """
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('role', User.Role.RENTER)
        
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
        Creates a superuser.

        Parameters:
        - email: Email address of the superuser.
        - username: Username of the superuser.
        - first_name: First name of the superuser.
        - password: Password for the superuser.
        - **other_fields: Additional fields for the superuser model.

        Returns:
        - Superuser instance.
        """
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('role', User.Role.ADMIN)

        if other_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff set to True")
        
        if other_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser set to True")
        
        return self.create_user(email, first_name, username, password, **other_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with support for different roles.
    """

    id = models.AutoField(primary_key=True)
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

    base_role = Role.RENTER

    role = models.CharField(max_length=50, choices=Role.choices)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'username']

    def has_permission(self, request, view):
        """
        Check if the user has permission for a specific view action.

        Parameters:
        - request: HTTP request object.
        - view: DRF view instance.

        Returns:
        - True if the user has permission, False otherwise.
        """
        if view.action == 'list' and not self.is_superuser:
            return False
        if view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            return str(request.user.id) == view.kwargs['pk']
        return True

    def __str__(self):
        """
        String representation of the user.

        Returns:
        - Full name of the user.
        """
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        """
        Save method for the user model.

        Sets the role to the base role if not provided.

        Returns:
        - Superuser instance.
        """
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


class RenterManager(BaseUserManager):
    """
    Custom manager for Renter model.
    """

    def create_user(self, email, username, first_name, password, **other_fields):
        """
        Creates a renter user.

        Parameters:
        - email: Email address of the renter.
        - username: Username of the renter.
        - first_name: First name of the renter.
        - password: Password for the renter.
        - **other_fields: Additional fields for the renter model.

        Returns:
        - Renter instance.
        """
        other_fields.setdefault('role', User.Role.RENTER)
        return super().create_user(email, username, first_name, password, **other_fields)


class Renter(User):
    """
    Custom Renter model inheriting from User.
    """

    base_role = User.Role.RENTER
    renter = RenterManager()

    institution = models.CharField(max_length=255, blank=False)
    phone_number = models.CharField(max_length=10, blank=False)
    registration_number = models.CharField(max_length=255, blank=False)


class Rent(models.Model):
    """
    Model representing a rental.
    """

    renter = models.ForeignKey(User, on_delete=models.CASCADE)
    rental_date = models.DateField()


class RenterProfile(models.Model):
    """
    Profile model for Renter.
    """

    user = models.OneToOneField(Renter, on_delete=models.CASCADE)
    renter_id = models.CharField(max_length=60, unique=True)
    last_rent_date = models.DateField(null=True, blank=True)
    max_rent_streak = models.IntegerField(default=0)

    def __str__(self):
        """
        String representation of the RenterProfile.

        Returns:
        - First name of the renter.
        """
        return self.user.first_name


@receiver(post_save, sender=Renter)
def create_renter_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to create a RenterProfile when a new Renter is created.
    """
    if created and instance.role == User.Role.RENTER:
        RenterProfile.objects.create(user=instance, renter_id=str(uuid4()), max_rent_streak=0)


@receiver(post_save, sender=Rent)
def update_rent_streak_on_rent(sender, instance, created, **kwargs):
    """
    Signal receiver to update the rent streak on the RenterProfile when a new Rent is created.
    """
    if created and instance.role == User.Role.RENTER:
        renter_profile = RenterProfile.objects.get(user=instance.renter)
        update_rent_streak(renter_profile)


def update_rent_streak(renter_profile):
    """
    Update the renter's rent streak based on the rental history.

    If the renter has rented consecutively, increment the streak; otherwise, reset it.

    Parameters:
    - renter_profile: RenterProfile instance.

    Returns:
    - None
    """
    today = renter_profile.last_rent_date

    if not today or today != renter_profile.last_rent_date:
        # If no previous rent date or today is different from the last rent date, set streak to 1
        renter_profile.max_rent_streak = 1
    else:
        yesterday = today - timedelta(days=1)
        if yesterday == renter_profile.last_rent_date:
            # If yesterday is the last rent date, increment the streak
            renter_profile.max_rent_streak += 1
        else:
            # If there is a gap in rental history, reset the streak to 0
            renter_profile.max_rent_streak = 0

    renter_profile.save()


class RenteeManager(BaseUserManager):
    """
    Custom manager for Rentee model.
    """

    def create_user(self, email, username, first_name, password, **other_fields):
        """
        Creates a rentee user.

        Parameters:
        - email: Email address of the rentee.
        - username: Username of the rentee.
        - first_name: First name of the rentee.
        - password: Password for the rentee.
        - **other_fields: Additional fields for the rentee model.

        Returns:
        - Rentee instance.
        """
        other_fields.setdefault('role', User.Role.RENTEE)
        return super().create_user(email, username, first_name, password, **other_fields)


class Rentee(User):
    """
    Custom Rentee model inheriting from User.
    """

    base_role = User.Role.RENTEE
    Rentee = RenteeManager()


class RenteeProfile(models.Model):
    """
    Profile model for Rentee.
    """

    user = models.OneToOneField(Rentee, on_delete=models.CASCADE)
    rentee_id = models.CharField(max_length=60, unique=True)

    def __str__(self):
        """
        String representation of the RenteeProfile.

        Returns:
        - Rentee ID.
        """
        return self.rentee_id


@receiver(post_save, sender=Rentee)
def create_rentee_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to create a RenteeProfile when a new Rentee is created.
    """
    if created and instance.role == User.Role.RENTEE:
        RenteeProfile.objects.create(user=instance, rentee_id=str(uuid4()))


class AdminsManager(BaseUserManager):
    """
    Custom manager for Administrator model.
    """

    def create_user(self, email, username, first_name, password, **other_fields):
        """
        Creates an admin user.

        Parameters:
        - email: Email address of the admin.
        - username: Username of the admin.
        - first_name: First name of the admin.
        - password: Password for the admin.
        - **other_fields: Additional fields for the admin model.

        Returns:
        - Administrator instance.
        """
        other_fields.setdefault('role', User.Role.ADMIN)
        return super().create_user(email, username, first_name, password, **other_fields)


class Administrator(User):
    """
    Custom Administrator model inheriting from User.
    """

    base_role = User.Role.ADMIN
    admin_manager = AdminsManager()

    joined_on = models.DateTimeField(default=timezone.now)
