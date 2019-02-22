from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    #path(r'^(?P<resource_id>[0-9]+)/$', views.index, name='index'),
    url(r'^(?P<resource_id>[0-9]+)/$', views.index, name='index'),

]
