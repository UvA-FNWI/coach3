from django.urls import path
from django.conf.urls import url

from . import views
#from .views import LTIToolConfigView

app_name = 'iki'
urlpatterns = [
    #path(r'^(?P<resource_id>[0-9]+)/$', views.index, name='index'),
    #url(r'^(?P<user_id>[0-9]+)/$', views.index, name='index'),
    path('<user_id>/', views.index, name='index'),
    path('<student_id>/new_goal', views.new_goal, name='new_goal'),
    #url(r'(\d+)/', views.index, name='index'),
    #url('', views.IndexView.as_view(), name='index'),
    # url(r'^launch$',views.lti_launch, name="launch"),
    # #url(r'^launch$',views.LTILaunchView.as_view(), name="launch"),
    # url(r'^config$', LTIToolConfigView.as_view(), name='config'),
]
