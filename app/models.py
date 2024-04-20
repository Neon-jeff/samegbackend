from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile',null=True,blank=True)
    is_property_owner=models.BooleanField(default=False)
    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name} Profile'



class Property(models.Model):
    location=models.CharField(max_length=400,null=False,blank=True)
    title=models.CharField(max_length=400,null=False,blank=True)
    price=models.IntegerField(default=0)
    description=models.TextField(max_length=3000,null=True,blank=True)
    image=models.URLField(null=False,blank=True)
    size=models.CharField(null=True,blank=True,max_length=400)

    def __str__(self) -> str:
        return f'{self.title} Property'

class User_Property(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,blank=False,null=False,related_name='properties')
    property=models.ForeignKey(Property,on_delete=models.CASCADE,blank=True,null=False)
    size_bought=models.CharField(null=True,blank=True,max_length=400)
    property_document=models.URLField(null=True,blank=True)
    property_amount=models.IntegerField(null=True,blank=True)
    paid_amount=models.IntegerField(default=0,null=True,blank=True)
    images=ArrayField(models.URLField(),null=True,blank=True)

# class UserPropertyImage(models.Model):
#     image=models.URLField(null=True,blank=True)
#     user_property=models.ForeignKey(User_Property,on_delete=models.CASCADE,related_name='images')

#     def __str__(self) -> str:
#         return f'{self.user_property.user.first_name} property Image'