from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(role_master)
class RoleMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')

@admin.register(role_url_permission)
class RoleUrlPermissionAdmin(admin.ModelAdmin):
    list_display = ('url', 'role_master','bln_get','bln_post','bln_put','bln_patch','bln_delete','status')

@admin.register(user_data)
class UserDataAdmin(admin.ModelAdmin):
    list_display = ('id','first_name', 'last_name', 'email', 'role_master','otp')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')

@admin.register(order_status)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(order_master)
class OrderMasterAdmin(admin.ModelAdmin):
    list_display = ('order_no','order_status','total_amt','delivery_agent','created_by','created_date','modified_by','modified_date' ,'int_status')

@admin.register(order_details)
class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = ('order_master','product','quantity','unit_price','amount','int_status')
