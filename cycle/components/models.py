from django.db import models
from uuid import uuid4
from users.models import User, Rentee, Renter
from django.utils import timezone

class BaseModel(models.Model):
    """
    Base Model where all commodity classes will inherit from.
    """
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Bike(BaseModel):
    """
    Model that handles creation of Bike instances.

    Fields:
    - owner: Renter who owns the bike.
    - rented_by: Rentee(s) who have rented the bike.
    - rented: Indicates whether the bike is currently rented.
    - brand: Brand of the bike.
    - rent_price: Price for renting the bike.
    """
    owner = models.ForeignKey(Renter, on_delete=models.CASCADE, related_name="bike_owner")
    rented_by = models.ManyToManyField(Rentee, related_name="bike_reentee")
    rented = models.BooleanField(default=False)
    brand = models.CharField(max_length=60, null=True)
    rent_price = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.id}.{self.brand} owned by {self.owner}'

class Wallet(BaseModel):
    """
    Model that handles creation of each User's wallet.

    Fields:
    - user: User associated with the wallet.
    - balance: Current balance in the wallet.
    - last_top_up: Date and time of the last wallet top-up.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)
    last_top_up = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.id}.{self.user}\'s Wallet'

class History(BaseModel):
    """
    Model that handles creation of rental history.

    Fields:
    - bike: Bike associated with the rental history.
    - rentee: Rentee involved in the rental.
    - renter: Renter involved in the rental.
    - amount_paid: Amount paid for the rental.
    - rental_start_time: Start time of the rental.
    - rental_end_time: End time of the rental.
    - rental_status: Type of rental event (Bike Rented, Bike Returned, Renter Rental, Rentee Rental).
    """
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

    rental_status = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.BIKE_RENTED,
    )
    
    @classmethod
    def log_bike_rental(cls, bike, rentee, renter, amount_paid, logged_in_user):
        """ 
        Log a bike rental event.

        Parameters:
        - bike: Bike instance.
        - rentee: Rentee instance.
        - renter: Renter instance.
        - amount_paid: Amount paid for the rental.
        - logged_in_user: User initiating the action.

        Returns:
        - History instance for the logged rental event.
        """
        if logged_in_user.role == 'RENTEE':
            history = cls.objects.create(
                bike=bike,
                rentee=rentee,
                renter=renter,
                amount_paid=amount_paid,
                rental_status=cls.EventType.BIKE_RENTED,
            )
            return history

    @classmethod
    def log_bike_return(cls, bike, logged_in_user):
        """ 
        Log a bike return event.

        Parameters:
        - bike: Bike instance.
        - logged_in_user: User initiating the action.

        Returns:
        - History instance for the logged return event.
        """
        if logged_in_user.role == 'RENTEE':
            history = cls.objects.create(
                bike=bike,
                rental_status=cls.EventType.BIKE_RETURNED,
            )
            return history

    @classmethod
    def log_renter_rental(cls, renter, amount_paid, logged_in_user):
        """ 
        Log a renter rental event.

        Parameters:
        - renter: Renter instance.
        - amount_paid: Amount paid for the rental.
        - logged_in_user: User initiating the action.

        Returns:
        - History instance for the logged rental event.
        """
        if logged_in_user.role == 'RENTER':
            history = cls.objects.create(
                renter=renter,
                amount_paid=amount_paid,
                rental_status=cls.EventType.RENTER_RENTAL,
            )
            return history

    @classmethod
    def log_rentee_rental(cls, rentee, amount_paid, logged_in_user):
        """ 
        Log a rentee rental event.

        Parameters:
        - rentee: Rentee instance.
        - amount_paid: Amount paid for the rental.
        - logged_in_user: User initiating the action.

        Returns:
        - History instance for the logged rental event.
        """
        if logged_in_user.role == 'RENTEE':
            history = cls.objects.create(
                rentee=rentee,
                amount_paid=amount_paid,
                rental_status=cls.EventType.RENTEE_RENTAL,
            )
            return history

class Notification(BaseModel):
    """
    Model for handling user notifications.

    Fields:
    - user: User associated with the notification.
    - content: Notification content.
    - read_status: Indicates whether the notification has been read.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    read_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification {self.id} - User: {self.user.username}, Content: {self.content}"

    @classmethod
    def create_notification(cls, user, content):
        """ 
        Create a new notification.

        Parameters:
        - user: User to whom the notification belongs.
        - content: Content of the notification.

        Returns:
        - Notification instance.
        """
        notification = cls.objects.create(user=user, content=content)
        return notification

    @classmethod
    def mark_as_read(cls, notification_id):
        """ 
        Mark a notification as read.

        Parameters:
        - notification_id: ID of the notification to mark as read.
        """
        notification = cls.objects.get(id=notification_id)
        notification.read_status = True
        notification.save()
