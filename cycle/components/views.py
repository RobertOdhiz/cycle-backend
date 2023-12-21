
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.shortcuts import get_object_or_404
from .models import Bike, History, Wallet, Notification
from users.models import Renter, Rentee
from .serializers import BikeSerializer, HistorySerializer, WalletSerializer, NotificationSerializer

class BikeListView(APIView):
    """
    Returns a list of all Bikes in the database
    """
    def get(self, request):
        """
        Function that handles the GET request
        """
        if request.user.role == Renter.base_role:
            bikes = Bike.objects.filter(owner=request.user)
        else:
            bikes = Bike.objects.all()

        bike_serializer = BikeSerializer(bikes, many=True)
        return Response(bike_serializer.data)

class HistoryListView(APIView):
    """
    Returns a list of all the History objects if the user is an Admin otherwise
    returns only the History for the specified user
    """
    def get(self, request):
        """ Handles the GET mathod """
        if request.user.role == Renter.base_role:
            history = History.objects.filter(renter=request.user)
        elif request.user.role == Rentee.base_role:
            history = History.objects.filter(rentee=request.user)
        else:
            history = History.objects.all()

        history_serializer = HistorySerializer(history, many=True)
        return Response(history_serializer.data)