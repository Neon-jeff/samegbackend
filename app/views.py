from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication,BasicAuthentication,TokenAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from .serializers import *
from django.contrib.auth import login,logout,authenticate
from .models import *
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.authtoken.models import Token
from rest_framework.validators import ValidationError,DataError
import json
from utils.upload import upload_image,upload_document,upload_user_property_image
from utils.temp_file import  create_temp_path
# Create your views here.

# ---API SPECS---
# Create Admin user
# Create users
# Create Properties
# Create properties for users 

class CreateUser(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        return Response({'detail':'register user'})
    def post(self,request):
        if User.objects.filter(email=request.data['email']).first() is not None:
            return Response({"error":"Email already used"}, status=400)
        serializer=CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            token=serializer.create(serializer.validated_data)
        else:
            raise ValidationError(detail={
                "error":"invalid data"
            },code=403)
        return Response({"token":token},status=201)

class Login(APIView):
    permission_classes = [AllowAny]
    def get(self,request):
        return Response({"user":"user"})
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.check_password(serializer.validated_data)
            if user is not None:
                token=Token.objects.get(user=user)
                return Response({"token":token.key,"id":user.id},status=200)
            else:
                return Response({"error":"Invalid login credentials"},status=400)
        return Response({"invalid":"login failed"},status=403   )


class CreateProperty(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[AllowAny]
    parser_classes=[MultiPartParser,FormParser]
    def get(self,request):
        _s=PropertySerializer(Property.objects.all(),many=True)
        return Response({"properties":_s.data},status=200)
    

    def post(self,request):
        _s=CreatePropertySerializer(data=request.data)
        if not request.user.is_superuser:
            return Response({"error":"User Not Authorised"})
        if not _s.is_valid():
            return Response({"detail":"Invalid Data"},status=403)
        path_dict=create_temp_path(request.FILES['image'])
        image_path=path_dict['path']
        image_name=path_dict['name']
        # upload image to boto3
        image_url=upload_image(image_path,image_name)
        Property.objects.create(
            location=request.data['location'],
            title=request.data['title'],
            description=request.data['description'],
            image=image_url,
            price=request.data['price'],
            size=request.data['size']
        )
        return Response({"data":'Property Created'},status=201)

class GetOneProperty(APIView):
    def get(self,request,pk):
        property_obj=Property.objects.filter(id=pk).first()
        if property_obj is None:
            return Response({"data":"No property found"},status=404)
        serializer=PropertySerializer(property_obj,many=False)
        return Response(serializer.data) 
    def patch(self,request,pk):
        property_obj=Property.objects.get(id=pk)
        serializer=PropertySerializer(property_obj,data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data) 

class CreateUserProperty(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAdminUser]
    parser_classes=[MultiPartParser,FormParser]
    def post(self,request):
        request.data['images']=request.data.pop('images[]')
        # data.pop('images[]',None)
        # _s=CreateUserPropertySerializer(data=request.data)
        # if not _s.is_valid():
        #     raise ValidationError(detail="Invalid Data",code=403)
        document_url=None
        image_list=[]
        if request.FILES.get('document') is not None:
            path_dict=create_temp_path(request.FILES['document'])
            document_path=path_dict['path']
            document_name=path_dict['name']  
            document_url=upload_document(document_path,document_name)
        if request.data.get('images') is not None:
            for file in request.data.get('images'):
                path_dict=create_temp_path(file)
                image_path=path_dict['path']
                image_name=path_dict['name']
                image_url=upload_user_property_image(image_path,image_name)
                image_list.append(image_url)
        User_Property.objects.create(
            user=User.objects.get(id=request.data['user_id']),
            property=Property.objects.get(id=request.data['property_id']),
            property_document=document_url,
            size_bought=request.data['size_bought'],
            paid_amount=request.data['paid_amount'],
            property_amount=request.data['property_amount'],
            images=image_list if len(image_list)>0 else None

        )
        User.objects.get(id=request.data['user_id']).profile.is_property_owner=True
        User.objects.get(id=request.data['user_id']).profile.save()

        return Response({"data":"User Property Creation Successful"},status=201)


class GetAllUser(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAdminUser]
    def get(self,request):
        result=[]
        users=User.objects.filter(is_superuser=False)
        for user in users:
            _p=ProfileSerializer(UserProfile.objects.get(user=user),many=False)
            _u=UserSerializer(user,many=False)
            data={**_u.data,**_p.data}
            result.append(data)
        return Response({"user":result})

class GetOneUser(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAdminUser]
    def get(self,request,pk):
        user=User.objects.filter(id=pk).first()
        if user is None:
            return Response({"error":"User does not exist"},status=404)
        
        serializer=UserSerializer(user,many=False)
        return Response({"data":serializer.data})


class GetProfile(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user=request.user
        _s=UserSerializer(request.user)
        serializer=ProfileSerializer(UserProfile.objects.get(user=user))
        return Response({"user":{**_s.data,**serializer.data}})

    def patch(self,request):
        profile_obj=User.objects.get(user=request.user)
        serializer=User(profile_obj,data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        

class LoginAdmin(APIView):
    
    def post(self,request):
        _s=AdminUserLogin(data=request.data)
        if not _s.is_valid():
            return Response({"error":"Invalid Data"},code=403)
        user=authenticate(username=_s.validated_data['username'],password=_s.validated_data['password'])
        if user is None:
            return Response({"error":"Invalid Login Details"},code=403)
        
        if not user.is_superuser:
            return Response({"error":"Not an admin user"},code=403)

        if  Token.objects.get(user=user) is  None:
            token=Token.objects.create(user=user)
            return Response({"token":token.key})
        token=Token.objects.get(user=user)
        return Response({"token":token.key})


class GetUserProperty(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user=request.user 
        user_properties=User_Property.objects.filter(user=user)
        _s=UserPropertySerializer(user_properties,many=True)
        return Response({"data":_s.data})
    

    
class GetOneUserProperty(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request,pk):
        user_property_obj=None
        try:
            user_property_obj=User_Property.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response({"error":"user property does not exist"},status=404)
            
        _s=UserPropertySerializer(user_property_obj,many=False)
        return Response({"data":_s.data})
        
    def patch(self,request,pk):
        property_obj=User_Property.objects.get(id=pk)
        serializer=UserPropertySerializer(property_obj,data=request.data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data) 
    # def post(self,request,pk):
    #     pass


    # helpers


