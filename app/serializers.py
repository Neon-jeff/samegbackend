from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['email','first_name','last_name','password']

    def create(self,data):
        if self.check_email_unique(data['email']):
            raise serializers.ValidationError(detail={"message":"Email already used"},code=403)
        new_user=User.objects.create(
            username=data['email'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            
        )
        new_user.set_password(data['password'])
        new_user.save()
        UserProfile.objects.create(user=new_user,is_property_owner=False)
        token=Token.objects.create(user=new_user)
        return token.key

    def check_email_unique(self,email):
        if User.objects.filter(email=email).first() is not None:
            return True
        else:
            return False
        
class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    password=serializers.CharField()

    def check_password(self,data):
        user=User.objects.filter(email=data['email']).first()
        if user is None:
            raise serializers.ValidationError(detail={"message":"No account with email found"},code=403)
        else:
            auth=authenticate(username=user.username,password=data['password'])
            return auth
        
class CreateUserPropertySerializer(serializers.Serializer):
    user_id=serializers.IntegerField()
    property_id=serializers.IntegerField()
    # document=serializers.FileField(required=False)
    property_amount=serializers.IntegerField()
    paid_amount=serializers.IntegerField()
    size_bought=serializers.CharField()
    images=serializers.ListField(child=serializers.FileField(),allow_empty=True)


class CreatePropertySerializer(serializers.Serializer):
    location=serializers.CharField()
    title=serializers.CharField()
    price=serializers.IntegerField()
    image=serializers.FileField()
    description=serializers.CharField()

class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model=Property
        fields='__all__'

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=['email','first_name','last_name','id']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserProfile
        fields=['is_property_owner']
    
class AdminUserLogin(serializers.Serializer):
    username=serializers.CharField()
    password=serializers.CharField()


# class PropertyImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=UserPropertyImage
#         fields=['image']


class UserPropertySerializer(serializers.ModelSerializer):
    user=UserSerializer()
    property=PropertySerializer()
    # images=serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     read_only=True
    # )
    class Meta:
        model=User_Property
        fields='__all__'

