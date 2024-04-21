from django.urls import path,include
from rest_framework.authtoken import views
from .views import *
urlpatterns = [
    
    path('get-token/',views.obtain_auth_token),
    path('signup/',CreateUser.as_view(),name='register'),
    path('login/',Login.as_view()),
    path('get-user/',GetProfile.as_view()),
    path('property/',CreateProperty.as_view()),
    path('user-property/',GetUserProperty.as_view()),
    path('user-property/<int:pk>/',GetOneUserProperty.as_view()),
    path('create-user-property/',CreateUserProperty.as_view()),
    path('login-admin/',LoginAdmin.as_view()),
    path('property/<int:pk>/',GetOneProperty.as_view()),
    path('all-users/',GetAllUser.as_view()),
    path('one-user/<int:pk>/',GetOneUser.as_view())

]