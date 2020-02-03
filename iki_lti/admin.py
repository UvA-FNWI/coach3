from django.contrib import admin
from iki.models import User, Course
# from simple_history.admin import SimpleHistoryAdmin
import os

from reversion.admin import VersionAdmin

@admin.register(User)
class YourModelAdmin(VersionAdmin):

    pass
# admin.site.register(User)
admin.site.register(Course)
# admin.site.register(User,SimpleHistoryAdmin)
# admin.site.register(SimpleHistoryAdmin)

def delete_model(modeladmin, request, queryset):
    for obj in queryset:
        filename=obj.profile_name+".xml"
        os.remove(os.path.join(obj.type,filename))
        obj.delete()

class profilesAdmin(admin.ModelAdmin):
    list_display = ["type","username","domain_name"]
    actions = [delete_model]