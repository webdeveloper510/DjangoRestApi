from django.contrib import admin
from .models import MakeUser,MakeCompany,MasterList,LocalLadder,CreateProject


# Register your models here.

admin.site.register(MakeUser)
admin.site.register(MakeCompany)
admin.site.register(LocalLadder)
admin.site.register(CreateProject)
admin.site.register(MasterList)
