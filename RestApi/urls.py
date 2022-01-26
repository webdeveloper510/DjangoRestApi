from django.contrib import admin
from django.urls import path,include
from RestApp.urls import path

urlpatterns = [
    path('',include('RestApp.urls')),
    path('admin/', admin.site.urls),
]
