# products models.py:

from django.db import models
from stores_app.models import store
from django.core.validators import MinValueValidator, MaxValueValidator

# product model:
class product(models.Model):
	store = models.ForeignKey(store, on_delete=models.SET_NULL, blank=True, null=True)
	name = models.CharField(max_length=81)
	price = models.IntegerField()
	WS_price = models.IntegerField(null=True, blank=True, default=121)
	choices = (('piece','piece'),('dozen','dozen'),('gross','gross'),('half gross','half gross'),('Kg','Kg'),('packet','packet')
				,('set','set'))
	unit = models.CharField(choices=choices,max_length=21,default='piece')
	tags = models.CharField(max_length=150,help_text='A list of comma seperated tags')
	available_qty = models.IntegerField(default=0)
	
	def __str__(self):
		return self.name

class customer(models.Model):
	name = models.CharField(max_length=81)
	addr = models.CharField(max_length=80)
	visit_freq = models.IntegerField(default=0)
	category = models.IntegerField(default=0)
	store_obj = models.ForeignKey(store, on_delete=models.SET_NULL, blank=True, null=True)

	def __str__(self):
		return str(self.name)

class bill_data(models.Model):
	store = models.ForeignKey(store, on_delete=models.SET_NULL, blank=True, null=True)
	b = models.CharField(max_length=5000)
	date_created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
	date_updated = models.DateTimeField(null=True, blank=True, auto_now=True)
	cust_obj = models.ForeignKey(customer, on_delete=models.SET_NULL, blank=True, null=True)
	
	def __str__(self):
		return str(self.id)