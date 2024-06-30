# login_app > urls.py

from . import views
from django.urls import path, include

urlpatterns = [
    path('',include('products.urls')),
    path('login/', views.login, name='login_page'),
    path('logout/', views.logout, name='logout_page'),
    path('register/', views.register, name='register_page'),
]
