from rest_framework import generics, permissions, status, authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password
from .models import User, Renter
from .serializers import UserSerializer, RenterSerializer
from .permissions import IsRenterOrReadOnly


class RenterCreateView(generics.CreateAPIView):
    """
    API view for creating Renter instances.

    Allows any user to create a Renter instance.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = RenterSerializer

    def perform_create(self, serializer):
        """
        Perform the creation of a Renter instance.

        Hashes the password before saving the user.

        Parameters:
        - serializer: RenterSerializer instance.
        """
        # Hash the password before saving the user
        serializer.save(password=make_password(serializer.validated_data['password']))


class RenterLoginView(TokenObtainPairView):
    """
    API view for handling Renter authentication and token generation.

    Inherits from TokenObtainPairView to handle token generation.
    """
    def post(self, request, *args, **kwargs):
        """
        Handle the POST request for Renter login.

        Extends the TokenObtainPairView post method and includes Renter ID in the response.

        Parameters:
        - request: HTTP request object.
        - *args: Additional positional arguments.
        - **kwargs: Additional keyword arguments.

        Returns:
        - Response object.
        """
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            renter = request.user
            response.data['id'] = renter.id
        return response


class UserListView(generics.ListAPIView):
    """
    API view for retrieving the list of all users in the system.

    Requires token authentication and is only visible to admins.
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer
