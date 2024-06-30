from django import template
from django.contrib.auth.models import Group 
  
register = template.Library() 
  
@register.filter(name='has_group')
def has_group(request, group_name):
    groups = [str(group) for group in request.user.groups.all()]
    return True if group_name in groups else False