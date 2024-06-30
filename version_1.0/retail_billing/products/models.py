# products models.py:

from django.db import models

# product model:
class product(models.Model):
	name = models.CharField(max_length=81)
	price = models.IntegerField()
	choices = (('piece','piece'),('dozen','dozen'),('gross','gross'),('half gross','half gross'),('Kg','Kg'),('packet','packet'))
	unit = models.CharField(choices=choices,max_length=21,default='piece')
	tags = models.CharField(max_length=150,help_text='A list of comma seperated tags')
	available_qty = models.IntegerField(default=0)
	
	def __str__(self):
		return self.name
        
class bill_data(models.Model):
    b = models.CharField(max_length=5000)
    date_created = models.DateTimeField(null=True, blank=True,auto_now_add=True)
    date_updated = models.DateTimeField(null=True, blank=True,auto_now=True)
    
    def __str__(self):
        return str(self.id)

