from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserListCreateView, RenterListCreateView

urlpatterns = [
    path('auth/token/', obtain_auth_token, name='obtain_token'),
    path('users/', UserListCreateView.as_view(), name='full-user-list'),
    path('users/renters/', RenterListCreateView.as_view(), name='renter-list'),
]
