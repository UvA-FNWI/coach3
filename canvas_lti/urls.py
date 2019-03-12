"""canvas_lti URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

#import django_app_lti.urls
import iki_lti.urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('iki/', include(('iki.urls', 'iki'), namespace="iki")),
    path('lti/', include(('iki_lti.urls', 'lti'), namespace = 'lti')),
     #url(r'^lti/', include(('iki_lti.urls', 'lti'), namespace="lti")),
     # url(r'^lti/', include((django_app_lti.urls, 'lti'), namespace="lti")),
     # #path('accounts/login/', include(django_app_lti.urls))
     # path('accounts/', include('django.contrib.auth.urls')),
]
