
from django.urls import path, include
from .views import UserAPI, userLogin, userLogout

urlpatterns = [
    # path('user_list', userList.as_view(), name='user_list'),
    path('', UserAPI.as_view(), name='user_api'),
    path('login', userLogin.as_view(), name='login'),
    path('logout', userLogout.as_view(), name='logout'),
]