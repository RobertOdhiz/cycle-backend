from django.contrib import admin
from .models import Bike, Wallet, History, Notification

admin.site.register(Bike)
admin.site.register(Wallet)
admin.site.register(History)
admin.site.register(Notification)