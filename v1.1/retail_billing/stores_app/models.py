# stores_app -> models.py
from django.db import models
from django.contrib.auth.models import User

# stores model:
class store(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    cash_value = models.IntegerField(default=0)
    activeFlag = models.CharField(max_length=1, default='Y')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True) # Store Owner

    def __str__(self):
        return self.name

# stores model:
class store_emp(models.Model):
    emp_obj = models.ForeignKey(User, on_delete=models.CASCADE)
    addr = models.CharField(max_length=80)
    activeFlag = models.CharField(max_length=1, default='Y')
    choices = (('store_manager','store_manager'),('store_staff','store_staff'))
    role = models.CharField(choices=choices, max_length=50, default='store_staff')
    store_obj = models.ForeignKey(store, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.emp_obj.username

