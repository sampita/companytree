from django.db import models

class Company(models.Model):
    '''Company Model'''
    name = models.CharField(max_length=50)

    class Meta:

        ordering = ("name", )
        verbose_name = ("company")
        verbose_name_plural = ("companies")