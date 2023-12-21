from rest_framework import (
    generics,
    permissions,
    status,
    authentication
    )
from rest_framework.views import APIView
from .models import User, Renter, Rent, RenterProfile, Rentee, RenteeProfile
from .serializers import UserSerializer, RenterSerializer
from .permissions import IsRenterOrReadOnly
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password


# class RenterCreateView(APIView):
#     """ Responsible for creation of all user instances """
#     permission_classes = [permissions.AllowAny]
#     def post(self, request):
#         """ Handles POST requests """
#         serializer = RenterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()

#             instance = serializer.data
#             return Response(RenterSerializer(instance).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def perform_create(self, serializer):
#         # Hash the password before saving the user
#         serializer.save(password=make_password(serializer.validated_data['password']))

class RenterCreateView(generics.CreateAPIView):
    """ Responsible for creation of all user instances """
    permission_classes = [permissions.AllowAny]
    serializer_class = RenterSerializer  # Set the serializer class directly

    def perform_create(self, serializer):
        # Hash the password before saving the user
        serializer.save(password=make_password(serializer.validated_data['password']))

class UserListView(generics.ListAPIView):
    """
    Returns the list of all users in the system

    * requires token authentication
    * Only visible to admins
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    queryset = User.objects.all()
    serializer_class = UserSerializer
