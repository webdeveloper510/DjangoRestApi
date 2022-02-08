from django.contrib import admin
from .models import MakeUser, MakeCompany, MasterList, LocalLadder, CreateProject


# Register your models here.

class MakeUserAdmin(admin.ModelAdmin):
    radio_fields = {'Active': admin.HORIZONTAL}


admin.site.register(MakeUser, MakeUserAdmin)


class MakeCompanyAdmin(admin.ModelAdmin):
    radio_fields = {'Active': admin.HORIZONTAL}


admin.site.register(MakeCompany, MakeCompanyAdmin)

admin.site.register(LocalLadder)
admin.site.register(CreateProject)
admin.site.register(MasterList)
