
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.shortcuts import get_object_or_404
from .models import Bike, History, Wallet, Notification
from users.models import Renter, Rentee, User
from .serializers import BikeSerializer, HistorySerializer, WalletSerializer, NotificationSerializer

class BikeListView(APIView):
    """
    Returns a list of all Bikes in the database
    """
    def get(self, request):
        """
        Function that handles the GET request
        """
        if request.user.role == User.Role.RENTER:
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

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """ Handles the GET mathod """
        if request.user.role == User.Role.RENTER:
            history = History.objects.filter(renter=request.user)
        elif request.user.role == User.Role.RENTEE:
            history = History.objects.filter(rentee=request.user)
        else:
            history = History.objects.all()

        history_serializer = HistorySerializer(history, many=True)
        return Response(history_serializer.data, status=200)
    
class HistoryCreateView(APIView):
    """ Object for creating, deleting, and updating the History objects in the database """

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    def post(self, request):
        """ Handles the POST http method """
        serializer = HistorySerializer(data=request.data)
        if serializer.is_valid():
            if request.user.role == User.Role.RENTER:
                serializer.save(renter=request.user)
            if request.user.role == User.Role.RENTEE:
                serializer.save(rentee=request.user)
            created_instance = serializer.instance

            # Return the serialized data of the created instance
            return Response(HistorySerializer(created_instance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """ Handles the PUT http method for updating a History instance """
        history_instance = self.get_object(pk)
        serializer = HistorySerializer(history_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """ Handles the DELETE http method for deleting a History instance """
        history_instance = self.get_object(pk)
        history_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self, pk):
        """ Helper method to get a History instance by its primary key """
        try:
            return History.objects.get(pk=pk)
        except History.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)