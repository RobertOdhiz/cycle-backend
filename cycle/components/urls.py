from django.urls import path
from .views import BikeListView, HistoryListView

urlpatterns = [
    path('bikes/', BikeListView.as_view(), name='bike-list'),
    path('history/', HistoryListView.as_view(), name='history-list')
]
