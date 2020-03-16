from django.db import models

class Department(models.Model):
    '''Department Model'''
    name = models.CharField(max_length=50)
    colorHex = models.CharField(max_length=50)

    class Meta:

        ordering = ("name", )
        verbose_name = ("department")
        verbose_name_plural = ("departments")