from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, email, username, first_name, password, **other_fields):

        other_fields.setdefault('is_active', True)

        if not email:
            raise ValueError("Please enter an email address")
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name, **other_fields)

        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, email, username, first_name, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff set to True")
        
        if other_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser set to True")
        
        return self.create_user(email, first_name, username, password, **other_fields)


        

class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    username= models.CharField(max_length=255, unique=True, null=True)
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
    REQUIRED_FIELDS = ['username','first_name']

    def __str__(self):
        return self.first_name
    
    def natural_key(self):
        return (self.username,)

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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    renter_id = models.CharField(max_length=10, unique=True)
    last_rent_date = models.DateField(null=True, blank=True)
    max_rent_streak = models.IntegerField(default=0)


@receiver(post_save, sender=Renter)
def create_renter_profile(sender, instance, created, **kwargs):
    if created and instance.role == "RENTER":
        RenterProfile.objects.create(user=instance, renter_id=generate_renter_id(), max_rent_streak=0)

@receiver(post_save, sender=Rent)
def update_rent_streak_on_rent(sender, instance, created, **kwargs):
    if created:
        renter_profile = RenterProfile.objects.get(user=instance.renter)
        update_rent_streak(renter_profile)


class RenteeManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.RENTEE)


class Rentee(User):
    base_role = User.Role.RENTEE

    Rentee = RenteeManager()

    class Meta:
        proxy = True


class RenteeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    renter_id = models.CharField(max_length=10, unique=True)


@receiver(post_save, sender=Rentee)
def create_renter_profile(sender, instance, created, **kwargs):
    if created and instance.role == "RENTEE":
        RenteeProfile.objects.create(user=instance, renter_id=generate_renter_id())


def generate_renter_id():
    last_renter_profile = RenterProfile.objects.last()

    MAX_NUMBER = 9999
    START_LETTER = "A"

    if last_renter_profile:
        cycle, number_str = last_renter_profile.renter_id.split("-")

        number = int(number_str) + 1

        if number > MAX_NUMBER:
            cycle = chr((ord(cycle) - ord(START_LETTER) + 1) % 26 + ord(START_LETTER))
            number = 1

    else:
        cycle = START_LETTER
        number = 1

    new_renter_id = f"{cycle}-{number:04d}"

    return new_renter_id

def update_rent_streak(renter_profile):
    today = renter_profile.last_rent_date

    if not today or today != renter_profile.last_rent_date:
        renter_profile.max_rent_streak = 1
    else:
        yesterday = today - timedelta(days=1)
        if yesterday == renter_profile.last_rent_date:
            renter_profile.max_rent_streak += 1
        else:
            renter_profile.max_rent_streak = 1
