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
from rest_framework.generics import *
from utils.upload import upload_image,upload_document,upload_user_property_image,delete_files
from utils.temp_file import  create_temp_path
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# Create your views here.

# ---API SPECS---
# Create Admin user
# Create users
# Create Properties
# Create properties for users 

class CreateUser(APIView):
    permission_classes = [AllowAny]
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
    
    @swagger_auto_schema(
    # method='post',
    request_body=openapi.Schema(
        operation_description="Log in with email and password for access token",
        type=openapi.TYPE_OBJECT,
        properties={
            'password': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['name', 'email']
    ),
    responses={
        201: 'Created',
        400: 'Bad Request',
    }
)    
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.check_password(serializer.validated_data)
            if user is not None:
                token=Token.objects.get(user=user)
                return Response({"token":token.key,"id":user.id},status=201)
            else:
                return Response({"error":"Invalid login credentials"},status=400)
        return Response({"invalid":"login failed"},status=403   )


class CreateProperty(APIView):

    authentication_classes=[TokenAuthentication]
    permission_classes=[AllowAny]
    parser_classes=[MultiPartParser,FormParser]
    @swagger_auto_schema(
            operation_description="Get all created property",
            
            
    )    
    def get(self,request):
        _s=PropertySerializer(Property.objects.all(),many=True)
        return Response({"properties":_s.data},status=200)
    
    @swagger_auto_schema(
            operation_description="Create property",
            
            
    )
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
        instance=User_Property.objects.create(
            user=User.objects.get(id=request.data['user_id']),
            property=Property.objects.get(id=request.data['property_id']),
            property_document=document_url,
            size_bought=request.data['size_bought'],
            paid_amount=request.data['paid_amount'],
            property_amount=request.data['property_amount'],
            images=image_list if len(image_list)>0 else None

        )
        if request.FILES.get('document') is not None:
            path_dict=create_temp_path(request.FILES['document'])
            document_path=path_dict['path']
            document_name=path_dict['name']  
            document_url=upload_document(document_path,document_name)
            instance.property_document=document_url
            instance.save()
        if request.data.get('images') is not None:
            for file in request.data.get('images'):
                path_dict=create_temp_path(file)
                image_path=path_dict['path']
                image_name=path_dict['name']
                image_url=upload_user_property_image(image_path,image_name)
                image_list.append(image_url)
            instance.images=image_list
            instance.save()
        instance.save()
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

class GetOneUser(RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAdminUser]
    queryset=User.objects.all()
    serializer_class=UserSerializer


class GetProfile(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def get(self,request):
        user=request.user
        _s=UserSerializer(request.user)
        serializer=ProfileSerializer(UserProfile.objects.get(user=user))
        return Response({"data":{**_s.data,**serializer.data}})

    def patch(self,request):
        profile_obj=User.objects.get(user=request.user)
        serializer=UserSerializer(profile_obj,data=request.data,partial=True)
        if not serializer.is_valid(raise_exception=True):
            return Response({"error":"Invalid Data"},status=400)
        serializer.save()
        return Response({"data":serializer.data},status=200)

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
    @swagger_auto_schema(
            operation_description="Get all the properties for logged in user, in the client side"
    )
    def get(self,request):
        user=request.user 
        user_properties=User_Property.objects.filter(user=user)
        _s=UserPropertySerializer(user_properties,many=True)
        return Response({"data":_s.data})
    

    
# class GetOneUserProperty(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes=[IsAuthenticated]
#     def get(self,request,pk):
#         user=None
#         try:
#             user=User.objects.get(id=pk)
#         except ObjectDoesNotExist:
#             return Response({"error":"user does not exist"},status=404)
#         user_properties=User_Property.objects.filter(user=user)  
#         _s=UserPropertySerializer(user_properties,many=False)
#         return Response({"data":_s.data})

        

class EditUserProperty(RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAdminUser]
    queryset=User_Property.objects.all()
    serializer_class=UserPropertySerializer
    def perform_destroy(self, instance):
        if instance.property_document != None and instance.property_document !='':
            document_name_arr=instance.property_document.split('/')
            document_name=f'property-documents/{document_name_arr[-1]}'
            delete_files([document_name])
        
        if  instance.images is not None:
            image_list=[f"user-property-images/{image.split('/')[-1]}" for image in instance.images]
            delete_files(image_list)
        return super().perform_destroy(instance)



    # helpers

class GetAllUserProperty(ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAuthenticated]
    queryset=User_Property.objects.all()
    serializer_class=UserPropertySerializer

class EditProperty(RetrieveUpdateDestroyAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes=[IsAdminUser]
    queryset=Property.objects.all()
    serializer_class=PropertySerializer

    def perform_destroy(self, instance):
        if instance.image != None and instance.image !='':
            document_name_arr=instance.image.split('/')
            document_name=f'property-images/{document_name_arr[-1]}'
            delete_files([document_name])

        return super().perform_destroy(instance)

class UserPropertyByUserID(APIView):
    def get(self,request,pk):
        user=User.objects.filter(id=pk).first()
        if user is None:
            return Response({"error":"user does not exist"},status=404)
        user_properties=User_Property.objects.filter(user=user)
        _s=UserPropertySerializer(user_properties,many=True)
        return Response(_s.data,status=200)
