from rest_framework import generics, permissions
from rest_framework.views import APIView
from .models import User, Renter, Rent, RenterProfile, Rentee, RenteeProfile
from .serializers import UserSerializer, RenterSerializer
from .permissions import IsRenterOrReadOnly

class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class RenterListCreateView(generics.ListCreateAPIView):
    queryset = Renter.renter.all()
    serializer_class = RenterSerializer
    permission_classes = [IsRenterOrReadOnly]


class RenterCreateView(APIView):
    queryset = Renter.renter.all()
    serializer_class = RenterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, post):
        if request.user == 'POST':
            pass
