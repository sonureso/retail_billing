from django.contrib import admin
from .models import product,bill_data

@admin.register(product)
class productAdmin(admin.ModelAdmin):
	list_display =  ('id','name','price','unit','available_qty','tags')
	list_editable = ('available_qty',)
    
@admin.register(bill_data)
class bill_dataAdmin(admin.ModelAdmin):
	list_display = ('id','date_created','date_updated','b')
	#list_editable = ('status',)