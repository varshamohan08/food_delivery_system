
from django.urls import path, include
from .views import *

urlpatterns = [
    path('products_api', ProductAPI.as_view(), name='products_api'),
    path('order_api', OrderAPI.as_view(), name='order_api'),
]