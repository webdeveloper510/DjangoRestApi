from unicodedata import name
from django.urls import re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    # CreateUserAPIView,
    AddManualRequest,
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
    #AddTradeRequest,
    TeamRequest,
    DeleteAddTradeRequest,
    TeamsRequest,
    CheckMasterlistrequest,
    GetTradeRequest,
    add_trade_v2_request,
    PriorityPickrRequest,
    GetPlayer,
    Gettradev2Req,
    Get_Rounds_Pick,
    GetPickType,
    AcademyBidRequest,
    GetRounds,
    ConstraintsRquest,
    GetFlagPicks,
    GetFlagsRequest,
    add_FA_compansation_request,
    add_FA_compensation_v2,
    academy_bid_v2,
    add_nga_bid,
    dataframerequest,
    add_father_son,
    add_draft_night_selection,
    add_potential_trade,
    add_trade_v3,
    add_priority_pick_v2
)

urlpatterns = [

    # ############# POST URl"S ##########################
    re_path(r'^create-User/$', CreateUserAPIView.as_view()),
    re_path(r'^Auth/$', authenticate_user),
    re_path(r'^CreateProject/$', ProjNameDescRequest),
    re_path(r'^LocalLadder/$', LocalLadderRequest),
    re_path(r'^MasterList/$', CreateMasterListRequest),
    #re_path(r'^Add-Trade/$', AddTradeRequest),
    re_path(r'^MakeCompany/$', MakeCompanyRequest),
    re_path(r'^add_trade_v2/$', add_trade_v2_request),
    re_path(r'^Priority-Pick/$', PriorityPickrRequest),
    re_path(r'^Academy-Bid/(?P<pk>[0-9]+)$', AcademyBidRequest),
    re_path(r'^Academy-Bid-v2/(?P<pk>[0-9]+)$', academy_bid_v2),
    re_path(r'^Add-FA-Compansation/(?P<pk>[0-9]+)$', add_FA_compansation_request),
    re_path(r'^Add-FA-Compansation_v2/(?P<pk>[0-9]+)$', add_FA_compensation_v2),
    re_path(r'^Add-nga-bid/(?P<pk>[0-9]+)$', add_nga_bid),
    re_path(r'^df/(?P<pk>[0-9]+)$', dataframerequest),
    re_path(r'^add-add_father_son/(?P<pk>[0-9]+)$', add_father_son),
    re_path(r'^add-draft-night-selection/(?P<pk>[0-9]+)$', add_draft_night_selection),
    re_path(r'^add_trade_v3/(?P<pk>[0-9]+)$', add_trade_v3),
    re_path(r'^add_priority_pick_v2/(?P<pk>[0-9]+)$', add_priority_pick_v2),

    # #################### Update URL's #################

    re_path(r'^(?P<pk>[0-9]+)$', update_masterlist),
    re_path(r'^Add-Manual/(?P<pk>[0-9]+)$', AddManualRequest),
    

    # ####################### GET Urls's ################################

    re_path(r'^ShowMasterList/(?P<pk>[0-9]+)$', GETMasterListRequest),
    re_path(r'^ShowProject/$', GETProjectRequest),
    re_path(r'^Logout/$', LogoutRequest),
    re_path(r'^AddTeam/$', AddTeamRequest),
    re_path(r'^ShowCompany/$', CompanyListRequest),
    re_path(r'^ListOfUsers/$', UserListRequest),
    # url(r'^Transactions/$', TransactionsRequest),
    re_path(r'^Ladder/$', LadderRequest),
    re_path(r'^Show-Team/$', TeamRequest),
    re_path(r'^ShowProjectDetails/(?P<pk>[0-9]+)$', ProjectDetailsRequest),
    re_path(r'^Teams/$', TeamsRequest), 
    re_path(r'^Test-Masterlist/$', CheckMasterlistrequest),
    re_path(r'^Get-Trade/(?P<pk>[0-9]+)$', GetTradeRequest),
    re_path(r'^Get-Players/$', GetPlayer),
    re_path(r'^Get-Trade-v2/(?P<pk>[0-9]+)$', Gettradev2Req),
    re_path(r'^Rounds-Pick/(?P<pk>[0-9]+)$', Get_Rounds_Pick),
    re_path(r'^Constraint/(?P<pk>[0-9]+)$', ConstraintsRquest),
    re_path(r'^PickTypes/$',GetPickType),
    re_path(r'^Get-Rounds/$',GetRounds),
    re_path(r'^Get-FlagPicks/(?P<pk>[0-9]+)$',GetFlagPicks),
    re_path(r'^Get-Flags/$',GetFlagsRequest),


    # ################ Delete URL's ##########################
    re_path(r'^Delete-Team/(?P<pk>[0-9]+)$', DeleteTeamRequest),
    re_path(r'^Delete-Company/(?P<pk>[0-9]+)$', DeleteCompanyRequest),
    re_path(r'^DeleteMasterList/(?P<pk>[0-9]+)$', DeleteMasterListRequest),
    re_path(r'^DeleteLocalLadder/(?P<pk>[0-9]+)$', DeleteLocalLadderRequest),
    re_path(r'^DeleteProject/(?P<pk>[0-9]+)$', DeleteProjectRequest),
    re_path(r'^DeleteLadder/(?P<pk>[0-9]+)$', DeleteLadderRecordRequest),
    re_path(r'^DeleteTrade/(?P<pk>[0-9]+)$', DeleteAddTradeRequest),
    
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
