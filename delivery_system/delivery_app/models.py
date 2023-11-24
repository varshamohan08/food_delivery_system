from django.db.models.fields import TextField, EmailField, CharField, IntegerField, BooleanField, BigIntegerField, FloatField, DateTimeField
from django.db.models import JSONField, Model, ForeignKey, CASCADE, ImageField
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class role_master(Model):
    name = CharField(max_length=50,null=False,blank=False)
    status = IntegerField()

class role_url_permission(Model):
    url = CharField(max_length=50,null=False,blank=False)
    role_master = ForeignKey(role_master, on_delete=CASCADE)
    bln_get = BooleanField(default=True)
    bln_post = BooleanField(default=True)
    bln_put = BooleanField(default=True)
    bln_patch = BooleanField(default=True)
    bln_delete = BooleanField(default=True)
    status = IntegerField()


class user_data(Model):
    first_name = CharField(max_length=50,null=False,blank=False)
    last_name = CharField(max_length=50,null=False,blank=False)
    password = CharField(max_length=50)
    email = EmailField(blank= False, null= False, unique=True)
    user = ForeignKey(User, on_delete=CASCADE)
    role_master = ForeignKey(role_master, on_delete=CASCADE)
    phone_number = BigIntegerField()
    otp = IntegerField(null=True,blank=True)
    bln_active = BooleanField(default=True)

class products(Model):
    name = CharField(max_length=50,null=False,blank=False)
    description = TextField(null=True, blank=True)
    image = ImageField(upload_to='images/')
    unit_price =  FloatField()
    created_by = ForeignKey(user_data, on_delete=CASCADE, related_name="product_created_by")
    created_date = DateTimeField(default=timezone.now)
    modified_by = ForeignKey(user_data, on_delete=CASCADE, related_name="product_modified_by")
    modified_date = DateTimeField(default=timezone.now)
    bln_active = BooleanField(default=True)
    int_status = IntegerField(default=1)

class order_status(Model):
    name = CharField(max_length=50,null=False,blank=False)

class order_master(Model):
    order_no = CharField(max_length=50,null=False,blank=False)
    order_status = ForeignKey(order_status, on_delete=CASCADE, related_name="delevery_agent")
    total_amt =  FloatField(null=True, blank=True)
    customer = ForeignKey(user_data, on_delete=CASCADE, related_name="customer", null=True, blank=True)
    delivery_agent = ForeignKey(user_data, on_delete=CASCADE, related_name="delevery_agent", null=True, blank=True)
    created_by = ForeignKey(user_data, on_delete=CASCADE, related_name="order_master_created_by")
    created_date = DateTimeField(default=timezone.now)
    modified_by = ForeignKey(user_data, on_delete=CASCADE, related_name="order_master_modified_by")
    modified_date = DateTimeField(default=timezone.now)
    int_status = IntegerField(default=1)

class order_details(Model):
    order_master = ForeignKey(order_master, on_delete=CASCADE)
    product = ForeignKey(products, on_delete=CASCADE)
    quantity = IntegerField(default=1)
    unit_price =  FloatField()
    amount =  FloatField()
    int_status = IntegerField(default=1)