from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class role_master(models.Model):
    name = models.CharField(max_length=50,null=False,blank=False)
    status = models.IntegerField()

class role_url_permission(models.Model):
    url = models.CharField(max_length=50,null=False,blank=False)
    role_master = models.ForeignKey(role_master, on_delete=models.CASCADE)
    bln_get = models.BooleanField(default=True)
    bln_post = models.BooleanField(default=True)
    bln_put = models.BooleanField(default=True)
    bln_patch = models.BooleanField(default=True)
    bln_delete = models.BooleanField(default=True)
    status = models.IntegerField()


class user_data(models.Model):
    first_name = models.CharField(max_length=50,null=False,blank=False)
    last_name = models.CharField(max_length=50,null=False,blank=False)
    password = models.CharField(max_length=50)
    email = models.EmailField(blank= False, null= False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_master = models.ForeignKey(role_master, on_delete=models.CASCADE)
    phone_number = models.BigIntegerField()
    otp = models.IntegerField(null=True,blank=True)
    bln_active = models.BooleanField(default=True)