from django.contrib import admin
from django.urls import path, include
import users.urls
import components.urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include(users.urls)),
    path("components/", include(components.urls)),
]
