from django.urls import path
from .views import (
    BikeListView,
    HistoryListView, 
    HistoryCreateView
)

urlpatterns = [
    path('bikes/', BikeListView.as_view(), name='bike-list'),
    path('history/', HistoryListView.as_view(), name='history-list'),
    path('history/create/', HistoryCreateView.as_view(), name='create-history'),
]
