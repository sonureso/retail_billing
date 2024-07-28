from django.contrib import admin
from .models import store,store_emp

@admin.register(store)
class storeAdmin(admin.ModelAdmin):
	list_display =  ('id','name','address','cash_value','activeFlag','creator')
	list_editable = ('activeFlag','cash_value')
    
@admin.register(store_emp)
class store_empAdmin(admin.ModelAdmin):
	list_display = ('id','emp_obj','addr','activeFlag','role','store_obj')
	list_editable = ('activeFlag','role','store_obj')
	search_fields = ('emp_obj__first_name',)
