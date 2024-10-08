# products urls.py:
from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='login_index'),
		path('home/', views.home, name="home_page"),	
        path('add/',views.add_product, name="add_product"),
        path('bill/',views.bill, name="bill"),
        path('customers/',views.cust_home, name="cust_home"),
        path('customers/upd_cust/',views.upd_cust, name="upd_cust"),
        path('prev_bill/',views.prev_bill, name="prev_bill"),
        # path('settings/',views.settings, name="settings"),
        path('upd/',views.upd, name="update"),
        
	]