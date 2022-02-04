
# from django.urls import pa

# from django.urls import path
from unicodedata import name
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import CreateUserAPIView, authenticate_user, LocalLadderRequest, ProjNameDescRequest, CreateMasterListRequest, UpdateMasterListRequest, GETLocalLadderRequest, GETMasterListRequest, GETProjectRequest, LogoutRequest, DeleteMasterListRequest,DeleteLocalLadderRequest,DeleteProjectRequest


urlpatterns = [
    url(r'^create/$', CreateUserAPIView.as_view()),
    url(r'^Auth/$', authenticate_user, name="Auth"),
    url(r'^CreateProject/$', ProjNameDescRequest, name="CreateProject"),
    url(r'^LocalLadder/$', LocalLadderRequest, name="LocalLadder"),
    url(r'^MasterList/$', CreateMasterListRequest, name="MasterList"),
    url(r'^UpdateMasterList/$', UpdateMasterListRequest, name="UpdateMasterList"),
    url(r'^ShowLocalLadder/$', GETLocalLadderRequest, name="ShowLocalLadder"),
    url(r'^ShowMasterList/$', GETMasterListRequest, name="ShowMasterList"),
    url(r'^ShowProject/$', GETProjectRequest, name="ShowProject"),
    url(r'^Logout/$', LogoutRequest, name="Logout"),
    url(r'^DeleteMasterList/$', DeleteMasterListRequest, name="DeleteMasterLixst"),
    url(r'^DeleteLocalLadder/$<str:pk>/', DeleteLocalLadderRequest, name="DeleteLocalLadder"),
    url(r'^DeleteProject/$<str:pk>/', DeleteProjectRequest, name="DeleteProject"),

]
