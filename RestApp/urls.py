from unicodedata import name
from django.urls import re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    CreateUserAPIView,
    AddManualRequest,
    authenticate_user,
    LocalLadderRequest,
    Create_Project,
    CreateMasterListRequest,
    update_masterlist,
    GETMasterListRequest,
    GETProjectRequest, LogoutRequest,
    DeleteMasterListRequest,
    DeleteLocalLadderRequest,
    DeleteProjectRequest,
    CreateCompany,
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
    # AddTradeRequest,
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
    trade_optimiser_algorithm,
    GetFlagPicks,
    GetFlagsRequest,
    add_FA_compansation,
    add_FA_compensation_v2,
    academy_bid_v2,
    add_nga_bid,
    dataframerequest,
    add_father_son,
    add_draft_night_selection,
    add_trade_v3,
    add_priority_pick_v2,
    manual_pick_move,
    quick_academy_calculator,
    update_ladder,
    add_draftee_player,
    update_trade_offers,
    Visualisations,
    ConstraintsRquest,
    dashboard_request,
    delete_last_transaction_View
)

urlpatterns = [

    #  //////////////// POST URl"S ///////////////////////////

    re_path(r'^create-User/$', CreateUserAPIView.as_view()),
    re_path(r'^Auth/$', authenticate_user),
    re_path(r'^CreateProject/$', Create_Project),
    re_path(r'^LocalLadder/$', LocalLadderRequest),
    re_path(r'^MasterList/$', CreateMasterListRequest),
    re_path(r'^MakeCompany/$', CreateCompany),
    re_path(r'^add_trade_v2/(?P<pk>[0-9]+)$', add_trade_v2_request),
    re_path(r'^Priority-Pick/$', PriorityPickrRequest),
    re_path(r'^Academy-Bid/(?P<pk>[0-9]+)$', AcademyBidRequest),
    re_path(r'^Academy-Bid-v2/(?P<pk>[0-9]+)$', academy_bid_v2),
    re_path(r'^Add-FA-Compansation/(?P<pk>[0-9]+)$', add_FA_compansation),
    re_path(
        r'^add_FA_compensation_v2/(?P<pk>[0-9]+)$', add_FA_compensation_v2),
    re_path(r'^Add-nga-bid/(?P<pk>[0-9]+)$', add_nga_bid),
    re_path(r'^df/(?P<pk>[0-9]+)$', dataframerequest),
    re_path(r'^add_father_son/(?P<pk>[0-9]+)$', add_father_son),
    re_path(
        r'^add-draft-night-selection/(?P<pk>[0-9]+)$', add_draft_night_selection),
    re_path(r'^add_trade_v3/(?P<pk>[0-9]+)$', add_trade_v3),
    re_path(r'^manual_pick_move/(?P<pk>[0-9]+)$', manual_pick_move),
    re_path(
        r'^quick_academy_calculator/(?P<pk>[0-9]+)$', quick_academy_calculator),
    re_path(
        r'^Constraint/(?P<pk>\w+)/(?P<userid>[\w-]+)/$', ConstraintsRquest),
    re_path(r'^trade-alogrithm/(?P<pk>\w+)', trade_optimiser_algorithm),
    re_path(r'^update_ladder/(?P<pk>[0-9]+)$', update_ladder),
    re_path(r'^add-new-player/(?P<pk>[0-9]+)$', add_draftee_player),
    re_path(
        r'^Update_Trade_Offer/(?P<pk>[0-9]+)$', update_trade_offers),
    re_path(r'^Visualisations/(?P<pk>[0-9]+)$', Visualisations),

    # //////////////////////// Update URL's ////////////////////////

    re_path(r'^(?P<pk>[0-9]+)$', update_masterlist),
    re_path(r'^Manual-pick-insert/(?P<pk>[0-9]+)$', AddManualRequest),


    # ///////////////////////// GET Urls's /////////////////////////////////#

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
    re_path(r'^PickTypes/$', GetPickType),
    re_path(r'^Get-Rounds/$', GetRounds),
    re_path(r'^Get-FlagPicks/(?P<pk>[0-9]+)$', GetFlagPicks),
    re_path(r'^Get-Flags/$', GetFlagsRequest),
    re_path(r'^dashboard-api/(?P<pk>[0-9]+)$', dashboard_request),


    # ///////////////////////  Delete URL's /////////////////////////////////
    re_path(r'^Delete-Team/(?P<pk>[0-9]+)$', DeleteTeamRequest),
    re_path(r'^Delete-Company/(?P<pk>[0-9]+)$', DeleteCompanyRequest),
    re_path(r'^DeleteMasterList/(?P<pk>[0-9]+)$', DeleteMasterListRequest),
    re_path(r'^DeleteLocalLadder/(?P<pk>[0-9]+)$', DeleteLocalLadderRequest),
    re_path(r'^DeleteProject/(?P<pk>[0-9]+)$', DeleteProjectRequest),
    re_path(r'^DeleteLadder/(?P<pk>[0-9]+)$', DeleteLadderRecordRequest),
    re_path(r'^DeleteTrade/(?P<pk>[0-9]+)$', DeleteAddTradeRequest),
    re_path(
        r'^delete_last_transaction/(?P<pk>[0-9]+)$', delete_last_transaction_View),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
