from django.contrib import admin
from .models import User, Company, MasterList, LocalLadder, Project,AddTeam,DraftAnalyserTrade


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
