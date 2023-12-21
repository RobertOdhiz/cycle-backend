from django.urls import path
from .views import UserListView, RenterCreateView, RenterLoginView

urlpatterns = [
    path('users/', UserListView.as_view(), name='full-user-list'),
    path('users/create/renter/', RenterCreateView.as_view(), name='create-renter'),
    path('users/renter/login/', RenterLoginView.as_view(), name='renter-login'),
]
