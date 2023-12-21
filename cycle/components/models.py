# Assuming you are working within a Django view or API endpoint
from django.http import HttpResponse
from django.db import models
from uuid import uuid4
from users.models import User, Rentee, Renter

class BaseModel(models.Model):
    """
    Base Model where all commodity classes will inherit from
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Bike(BaseModel):
    """ Model that handles creation of Bike instances """
    owner = models.ForeignKey(Renter, on_delete=models.CASCADE, related_name="bike_owner")
    rented_by = models.ManyToManyField(Rentee, related_name="bike_reentee")
    rented = models.BooleanField(default=False)

class Wallet(BaseModel):
    """ Model that handles creation of each Users wallet """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)

class History(BaseModel):
    """ Model that handles creation of rental history """
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE, null=True, blank=True)
    rentee = models.ForeignKey(Rentee, on_delete=models.CASCADE, null=True, blank=True, related_name="rentee_history")
    renter = models.ForeignKey(Renter, on_delete=models.CASCADE, null=True, blank=True, related_name="renter_history")
    amount_paid = models.IntegerField(default=0)
    rental_start_time = models.DateTimeField(null=True, blank=True)
    rental_end_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"History {self.id}"

    class EventType(models.TextChoices):
        BIKE_RENTED = 'Bike Rented'
        BIKE_RETURNED = 'Bike Returned'
        RENTER_RENTAL = 'Renter Rental'
        RENTEE_RENTAL = 'Rentee Rental'

    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.BIKE_RENTED,
    )
    
    @classmethod
    def log_bike_rental(cls, bike, rentee, renter, amount_paid, logged_in_user):
        """ Log a bike rental event """
        if logged_in_user.role == 'RENTEE':
            history = cls.objects.create(
                bike=bike,
                rentee=rentee,
                renter=renter,
                amount_paid=amount_paid,
                event_type=cls.EventType.BIKE_RENTED,
            )
            return history


    @classmethod
    def log_bike_return(cls, bike, logged_in_user):
        """ Log a bike return event """
        if logged_in_user.role == 'RENTEE':
            history = cls.objects.create(
                bike=bike,
                event_type=cls.EventType.BIKE_RETURNED,
            )
            return history

    @classmethod
    def log_renter_rental(cls, renter, amount_paid, logged_in_user):
        """ Log a renter rental event """
        if logged_in_user.role == 'RENTER':
            history = cls.objects.create(
                renter=renter,
                amount_paid=amount_paid,
                event_type=cls.EventType.RENTER_RENTAL,
            )
            return history

    @classmethod
    def log_rentee_rental(cls, rentee, amount_paid, logged_in_user):
        """ Log a rentee rental event """
        if logged_in_user.role == 'RENTEE':
            history = cls.objects.create(
                rentee=rentee,
                amount_paid=amount_paid,
                event_type=cls.EventType.RENTEE_RENTAL,
            )
            return history

class Notification(BaseModel):
    """ Model for handling user notifications """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    read_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification {self.id} - User: {self.user.username}, Content: {self.content}"

    @classmethod
    def create_notification(cls, user, content):
        """ Create a new notification """
        notification = cls.objects.create(user=user, content=content)
        return notification

    @classmethod
    def mark_as_read(cls, notification_id):
        """ Mark a notification as read """
        notification = cls.objects.get(id=notification_id)
        notification.read_status = True
        notification.save()