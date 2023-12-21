from rest_framework import serializers
from .models import Bike, History, Wallet, Notification

class BikeSerializer(serializers.ModelSerializer):
    """ Serializes all Bike objects into JSON format """
    class Meta:
        model = Bike
        fields = '__all__'

class HistorySerializer(serializers.ModelSerializer):
    """ Serializes all History Objescts to JSON format """
    class Meta:
        model = History
        fields = '__all__'

class WalletSerializer(serializers.ModelSerializer):
    """ Serializes all Wallet objects into JSON format """
    class Meta:
        model = Wallet
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    """Serializes all Notification objects innto JSON format """
    class Meta:
        model = Notification
        fields = '__all__'