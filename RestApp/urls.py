
# from django.urls import pa

# from django.urls import path
from unicodedata import name
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import CreateUserAPIView, authenticate_user, LocalLadderRequest, ProjNameDescRequest, CreateMasterListRequest, UpdateMasterListRequest, GETLocalLadderRequest, GETMasterListRequest, GETProjectRequest, LogoutRequest, DeleteMasterListRequest,DeleteLocalLadderRequest,DeleteProjectRequest


urlpatterns = [
    url(r'^create/$', CreateUserAPIView.as_view()),
    url(r'^Auth/$', authenticate_user),
    url(r'^CreateProject/$', ProjNameDescRequest),
    url(r'^LocalLadder/$', LocalLadderRequest),
    url(r'^MasterList/$', CreateMasterListRequest),
    url(r'^UpdateMasterList/$', UpdateMasterListRequest),
    url(r'^ShowLocalLadder/$', GETLocalLadderRequest),
    url(r'^ShowMasterList/$', GETMasterListRequest),
    url(r'^ShowProject/$', GETProjectRequest),
    url(r'^Logout/$', LogoutRequest),
    url(r'^DeleteMasterList/(?P<pk>[0-9]+)$', DeleteMasterListRequest),
    url(r'^DeleteLocalLadder/(?P<pk>[0-9]+)$', DeleteLocalLadderRequest),
    url(r'^DeleteProject/(?P<pk>[0-9]+)$', DeleteProjectRequest),

]
