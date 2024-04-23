from django.urls import path,include
from rest_framework.authtoken import views
from .views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('user/signup/',CreateUser.as_view(),name='register'),
    path('user/login/',Login.as_view()),
    path('user/get-user/',GetProfile.as_view()),
    path('admin/property/',CreateProperty.as_view()),
    path('user/user-property/',GetUserProperty.as_view()),
    path('admin/all-user-property/',GetAllUserProperty.as_view()),
    path('admin/create-user-property/',CreateUserProperty.as_view()),
    path('admin/login-admin/',LoginAdmin.as_view()),
    path('admin/all-users/',GetAllUser.as_view()),
    path('admin/edit-user/<int:pk>/',GetOneUser.as_view()),
    path('admin/edit-user-property/<int:pk>/',EditUserProperty.as_view()),
    path('admin/edit-property/<int:pk>/',EditProperty.as_view())

]