from django.contrib import admin
from .models import product,bill_data,customer

@admin.register(product)
class productAdmin(admin.ModelAdmin):
	list_display =  ('id','name','price','WS_price','unit','available_qty','store','tags')
	list_editable = ('available_qty','price','WS_price')
    
@admin.register(bill_data)
class bill_dataAdmin(admin.ModelAdmin):
	list_display = ('id','store','cust_obj','b') # can be added -> 'date_created','date_updated'
	# list_editable = ('cust_obj',)

@admin.register(customer)
class customerAdmin(admin.ModelAdmin):
	list_display =  ('id','name','addr','visit_freq','category','store_obj')
	list_editable = ('name','addr','store_obj')