from django.urls import path
from . import views

urlpatterns = [
        path('', views.settings, name='settings'),
        path('upd_settings/', views.upd_settings, name="upd_settings"),
        path('get_user/', views.get_user, name="get_user"),
        path('get_user_for_manager/', views.get_user_for_manager, name="get_user"),
        path('get_store/', views.get_store, name="get_store"),
	]