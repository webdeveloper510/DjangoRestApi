from django.contrib import admin
from .models import (
    User,
    Company,
    MasterList,
    LocalLadder,
    Project,
    DraftAnalyserTrade,
    Players,
    AddTrade,
    PicksType,
    Teams,
    library_AFL_Draft_Points
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
admin.site.register(DraftAnalyserTrade)
admin.site.register(Players)
admin.site.register(AddTrade)
admin.site.register(PicksType)
admin.site.register(Teams)
admin.site.register(library_AFL_Draft_Points)