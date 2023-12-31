from rest_framework import serializers
from .models import User, Renter, Rent, RenterProfile, Rentee, RenteeProfile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'

class RenterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Renter
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password',
                  'institution', 'registration_number', 'phone_number', 'role']

# class UserSerializer():
#     pass

# class RenterSerializer():
#     pass