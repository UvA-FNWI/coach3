from django.contrib import admin
from iki.models import User
import os

admin.site.register(User)

def delete_model(modeladmin, request, queryset):
    for obj in queryset:
        filename=obj.profile_name+".xml"
        os.remove(os.path.join(obj.type,filename))
        obj.delete()

class profilesAdmin(admin.ModelAdmin):
    list_display = ["type","username","domain_name"]
    actions = [delete_model]