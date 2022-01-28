
# from django.urls import path
from unicodedata import name
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import CreateUserAPIView,authenticate_user


urlpatterns = [
    url(r'^create/$', CreateUserAPIView.as_view()),
    url(r'^Auth/$', authenticate_user,name="Auth"),
]
 