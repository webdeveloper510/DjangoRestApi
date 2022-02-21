from django.contrib import admin
from .models import (
    User,
    Company,
    MasterList,
    LocalLadder,
    Project,
    AddTeam,
    DraftAnalyserTrade,
    Players,
    AddTrade,
    PriorityPick,
    AcademyBid,
    FA_Compansations,
    ManualTeam,
    PicksType,
    LibraryAFLTeams
)


# Register your models here.

class MakeUserAdmin(admin.ModelAdmin):
    radio_fields = {'Active': admin.HORIZONTAL}


admin.site.register(User, MakeUserAdmin)


class MakeCompanyAdmin(admin.ModelAdmin):
    radio_fields = {'Active': admin.HORIZONTAL}


admin.site.register(Company, MakeCompanyAdmin)

admin.site.register(LocalLadder)
admin.site.register(Project)
admin.site.register(MasterList)
admin.site.register(AddTeam)
admin.site.register(DraftAnalyserTrade)
admin.site.register(Players)
admin.site.register(AddTrade)
admin.site.register(PriorityPick)
admin.site.register(AcademyBid)
admin.site.register(ManualTeam)
admin.site.register(FA_Compansations)
admin.site.register(PicksType)
admin.site.register(LibraryAFLTeams)