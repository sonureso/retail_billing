# main urls.py file:
from django.contrib import admin
from django.urls import path,include
from django.views.static import serve
## from django.conf.urls import url
from django.urls import re_path as url
from . import settings


urlpatterns = [
    path('',include('login_app.urls')),
    path('admin/', admin.site.urls),
	url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}), 
]
