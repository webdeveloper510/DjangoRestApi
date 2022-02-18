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
    ProjectDetailsRequest,
    CreateUserAPIView,
    DeleteTeamRequest,
    DeleteCompanyRequest,
    DeleteLadderRecordRequest,
    AddTradeRequest,
    AcademyBidRequest,
    PriorityPickRequest,
    ManualTeamRequest,
    FARequest
)

urlpatterns = [

    # ############# POST URl"S ##########################
    url(r'^create/$', CreateUserAPIView.as_view()),
    url(r'^Auth/$', authenticate_user),
    url(r'^CreateProject/$', ProjNameDescRequest),
    url(r'^LocalLadder/$', LocalLadderRequest),
    url(r'^MasterList/$', CreateMasterListRequest),
    url(r'^Add-Trade/$', AddTradeRequest),
    url(r'^Academy-Bid/$', AcademyBidRequest),
    url(r'^Priority-Pick/$', PriorityPickRequest),
    url(r'^Manual-Team/$', ManualTeamRequest),
    url(r'^FA-Compansation/$', FARequest),

    # #################### Update URL's #################

    url(r'^UpdateMasterList/$', UpdateMasterListRequest),

    # ####################### GET Urls's ################################
    
    url(r'^ShowMasterList/$', GETMasterListRequest),
    url(r'^ShowProject/$', GETProjectRequest),
    url(r'^Logout/$', LogoutRequest),
    url(r'^MakeCompany/$', MakeCompanyRequest),
    url(r'^AddTeam/$', AddTeamRequest),
    url(r'^ListOfCompany/$', CompanyListRequest),
    url(r'^ListOfUsers/$', UserListRequest),
    url(r'^Transactions/$', TransactionsRequest),
    url(r'^Ladder/$', LadderRequest),
    url(r'^ShowProjectDetails/(?P<pk>[0-9]+)$', ProjectDetailsRequest),

    # ################ Delete URL's ##########################
    url(r'^Delete-Team/(?P<pk>[0-9]+)$', DeleteTeamRequest),
    url(r'^Delete-Company/(?P<pk>[0-9]+)$', DeleteCompanyRequest),
    url(r'^DeleteMasterList/(?P<pk>[0-9]+)$', DeleteMasterListRequest),
    url(r'^DeleteLocalLadder/(?P<pk>[0-9]+)$', DeleteLocalLadderRequest),
    url(r'^DeleteProject/(?P<pk>[0-9]+)$', DeleteProjectRequest),
    url(r'^DeleteLadder/(?P<pk>[0-9]+)$', DeleteLadderRecordRequest),

]
