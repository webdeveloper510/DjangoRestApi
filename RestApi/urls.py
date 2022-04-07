from django.contrib import admin
from django.urls import re_path, include
from RestApp.urls import re_path

urlpatterns = [
   re_path('',include('RestApp.urls')),
   re_path('admin/', admin.site.urls),
]

    
