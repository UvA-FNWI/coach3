from django.urls import path
from django.conf.urls import url

from . import views
#from .views import LTIToolConfigView

app_name = 'iki'
urlpatterns = [
    path('<user_id>/', views.index, name='index'),
    path('<student_id>/new_goal', views.new_goal, name='new_goal'),
]
