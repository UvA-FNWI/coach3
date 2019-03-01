from django.contrib import admin
from iki_lti.models import MyLTICourse, MyLTICourseUser, MyLTIResource

# Register your models here.
admin.site.register(MyLTICourse)
admin.site.register(MyLTIResource)
admin.site.register(MyLTICourseUser)
