from unicodedata import name
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import (
    # CreateUserAPIView,
    authenticate_user,
    LocalLadderRequest,
    ProjNameDescRequest,
    CreateMasterListRequest,
    UpdateMasterListRequest,
    GETLocalLadderRequest,
    GETMasterListRequest,
    GETProjectRequest, LogoutRequest,
    DeleteMasterListRequest,
    DeleteLocalLadderRequest,
    DeleteProjectRequest,
    MakeCompanyRequest,
    AddTeamRequest,
    CompanyListRequest,
    UserListRequest,
    TransactionsRequest,
    LadderRequest,
    DeleteLadderRequest,
    ProjectDetailsRequest
)

urlpatterns = [
    # url(r'^create/$', CreateUserAPIView.as_view()),
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
    url(r'^MakeCompany/$', MakeCompanyRequest),
    url(r'^AddTeam/$', AddTeamRequest),
    url(r'^ListOfCompany/$', CompanyListRequest),
    url(r'^ListOfUsers/$', UserListRequest),
    url(r'^Transactions/$', TransactionsRequest),
    url(r'^Ladder/$', LadderRequest),
    url(r'^DeleteLadder/(?P<pk>[0-9]+)$', DeleteLadderRequest),
    url(r'^ShowProjectDetails/(?P<pk>[0-9]+)$', ProjectDetailsRequest),

]
