from django.contrib import admin
from django.conf.urls import url, include
from RestApp.urls import url

urlpatterns = [
    url('',include('RestApp.urls')),
    url('admin/', admin.site.urls),
]
