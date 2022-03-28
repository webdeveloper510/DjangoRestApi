from unicodedata import name
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import (
    # CreateUserAPIView,
    authenticate_user,
    LocalLadderRequest,
    ProjNameDescRequest,
    CreateMasterListRequest,
    update_masterlist,
    GETMasterListRequest,
    GETProjectRequest, LogoutRequest,
    DeleteMasterListRequest,
    DeleteLocalLadderRequest,
    DeleteProjectRequest,
    MakeCompanyRequest,
    AddTeamRequest,
    CompanyListRequest,
    UserListRequest,
    # TransactionsRequest,
    LadderRequest,
    ProjectDetailsRequest,
    CreateUserAPIView,
    DeleteTeamRequest,
    DeleteCompanyRequest,
    DeleteLadderRecordRequest,
    AddTradeRequest,
    TeamRequest,
    DeleteAddTradeRequest,
    TeamsRequest,
    CheckMasterlistrequest,
    GetTradeRequest,
    add_trade_v2_request,
    PriorityPickrRequest,
    GetPlayer,
    Gettradev2Req,
    Get_Rounds_Pick
)

urlpatterns = [

    # ############# POST URl"S ##########################
    url(r'^create-User/$', CreateUserAPIView.as_view()),
    url(r'^Auth/$', authenticate_user),
    url(r'^CreateProject/$', ProjNameDescRequest),
    url(r'^LocalLadder/$', LocalLadderRequest),
    url(r'^MasterList/$', CreateMasterListRequest),
    url(r'^Add-Trade/$', AddTradeRequest),
    url(r'^MakeCompany/$', MakeCompanyRequest),
    url(r'^add_trade_v2/$', add_trade_v2_request),
    url(r'^Priority-Pick/$', PriorityPickrRequest),

    # #################### Update URL's #################

    url(r'^UpdateMasterList/(?P<pk>[0-9]+)$', update_masterlist),

    # ####################### GET Urls's ################################

    url(r'^ShowMasterList/(?P<pk>[0-9]+)$', GETMasterListRequest),
    url(r'^ShowProject/$', GETProjectRequest),
    url(r'^Logout/$', LogoutRequest),
    url(r'^AddTeam/$', AddTeamRequest),
    url(r'^ShowCompany/$', CompanyListRequest),
    url(r'^ListOfUsers/$', UserListRequest),
    # url(r'^Transactions/$', TransactionsRequest),
    url(r'^Ladder/$', LadderRequest),
    url(r'^Show-Team/$', TeamRequest),
    url(r'^ShowProjectDetails/(?P<pk>[0-9]+)$', ProjectDetailsRequest),
    url(r'^Teams/$', TeamsRequest),
    url(r'^Test-Masterlist/$', CheckMasterlistrequest),
    url(r'^Get-Trade/(?P<pk>[0-9]+)$', GetTradeRequest),
    url(r'^Get-Players/$', GetPlayer),
    url(r'^Get-Trade-v2/(?P<pk>[0-9]+)$', Gettradev2Req),
    url(r'^Rounds-Pick/$', Get_Rounds_Pick),

    # ################ Delete URL's ##########################
    url(r'^Delete-Team/(?P<pk>[0-9]+)$', DeleteTeamRequest),
    url(r'^Delete-Company/(?P<pk>[0-9]+)$', DeleteCompanyRequest),
    url(r'^DeleteMasterList/(?P<pk>[0-9]+)$', DeleteMasterListRequest),
    url(r'^DeleteLocalLadder/(?P<pk>[0-9]+)$', DeleteLocalLadderRequest),
    url(r'^DeleteProject/(?P<pk>[0-9]+)$', DeleteProjectRequest),
    url(r'^DeleteLadder/(?P<pk>[0-9]+)$', DeleteLadderRecordRequest),
    url(r'^DeleteTrade/(?P<pk>[0-9]+)$', DeleteAddTradeRequest),
]
