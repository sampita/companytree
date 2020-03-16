from django.db import models

class EmployeeHobby(models.Model):
    '''EmployeeHobby Model'''
    hobby = models.CharField(max_length=50)
    employee = models.ForeignKey('Employee', on_delete=models.DO_NOTHING, related_name="hobbies")

    class Meta:

        ordering = ("employee", )
        verbose_name = ("hobby")
        verbose_name_plural = ("hobbies")