from django.conf.urls import url

#from .views import MyLTILaunchView, MyLTIResponse
#from .views import LaunchView
from . import views


urlpatterns = [
    url(r'^launch$',views.lti_launch, name="launch"),
    #url(r'^launch$',views.LTILaunchView.as_view(), name="launch"),
    url(r'^config$', views.LTIToolConfigView.as_view(), name='config'),
]
