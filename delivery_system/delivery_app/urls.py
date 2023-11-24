
from django.urls import path, include
from .views import *

urlpatterns = [
    # path('user_list', userList.as_view(), name='user_list'),
    path('login', userLogin.as_view(), name='login'),
    path('logout', userLogout.as_view(), name='logout'),
    path('user_api', UserAPI.as_view(), name='user_api'),
    path('products_api', ProductAPI.as_view(), name='products_api'),
    path('order_api', OrderAPI.as_view(), name='order_api'),
]