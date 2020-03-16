from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.expressions import F

class Employee(models.Model):
    '''Employee Model'''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.DO_NOTHING, null=True)
    supervisor = models.ForeignKey('Employee', on_delete=models.DO_NOTHING, null=True)
    position = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    bio = models.TextField(max_length=500)
    image_url = models.URLField(max_length=1000)
    tasks = models.CharField(max_length=500)
    phone = models.CharField(max_length=30)
    slack = models.CharField(max_length=30)
    is_admin = models.BooleanField()

    # def __str__(self):
    #     return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = (F('id').asc(nulls_last=True),)
        #Instances of F() act as a reference to a model field within a query. These references can then be used in query filters to compare the values of two different fields on the same model instance.
        
        #In this case, order by the date the user joined (by ascending) and null fields last.