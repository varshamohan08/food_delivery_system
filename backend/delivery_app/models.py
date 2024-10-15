from django.db import models
from django.utils import timezone
from user_app.models import user_data

# Create your models here.


class products(models.Model):
    name = models.CharField(max_length=50,null=False,blank=False)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/')
    unit_price = models. FloatField()
    created_by = models.ForeignKey(user_data, on_delete=models.CASCADE, related_name="product_created_by")
    created_date = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(user_data, on_delete=models.CASCADE, related_name="product_modified_by")
    modified_date = models.DateTimeField(default=timezone.now)
    bln_active = models.BooleanField(default=True)
    int_status = models.IntegerField(default=1)

class order_status(models.Model):
    name = models.CharField(max_length=50,null=False,blank=False)

class order_master(models.Model):
    order_no = models.CharField(max_length=50,null=False,blank=False)
    order_status = models.ForeignKey(order_status, on_delete=models.CASCADE, related_name="delevery_agent")
    total_amt = models. FloatField(null=True, blank=True)
    customer = models.ForeignKey(user_data, on_delete=models.CASCADE, related_name="customer", null=True, blank=True)
    delivery_agent = models.ForeignKey(user_data, on_delete=models.CASCADE, related_name="delevery_agent", null=True, blank=True)
    created_by = models.ForeignKey(user_data, on_delete=models.CASCADE, related_name="order_master_created_by")
    created_date = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(user_data, on_delete=models.CASCADE, related_name="order_master_modified_by")
    modified_date = models.DateTimeField(default=timezone.now)
    int_status = models.IntegerField(default=1)

class order_details(models.Model):
    order_master = models.ForeignKey(order_master, on_delete=models.CASCADE)
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.FloatField()
    amount = models.FloatField()
    int_status = models.IntegerField(default=1)