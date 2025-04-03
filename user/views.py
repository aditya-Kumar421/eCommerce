from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, LoginSerializer
from .utils import generate_token
from pymongo import MongoClient
from django.conf import settings
import bcrypt
db_client = MongoClient(settings.MONGO_URI)
db = db_client["eCommerce"]  # Replace with your actual DB name
users_collection = db["users"]

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            
            # Check if user already exists
            if db.users.find_one({'email': serializer.validated_data['email']}):
                return Response({'error': 'Email already exists'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Hash password
            hashed_password = bcrypt.hashpw(
                serializer.validated_data['password'].encode('utf-8'),
                bcrypt.gensalt()
            )
            
            # Create user document
            user_data = {
                'username': serializer.validated_data['username'],
                'email': serializer.validated_data['email'],
                'password': hashed_password,
                'role': serializer.validated_data['role']
            }
            
            result = db.users.insert_one(user_data)
            user_id = str(result.inserted_id)
            token = generate_token(user_id, user_data['role'])
            
            return Response({
                'token': token,
                'user_id': str(result.inserted_id)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            
            user = db.users.find_one({'email': serializer.validated_data['email']})
            if not user:
                return Response({'error': 'Invalid credentials'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            
            if not bcrypt.checkpw(
                serializer.validated_data['password'].encode('utf-8'),
                user['password']
            ):
                return Response({'error': 'Invalid credentials'}, 
                              status=status.HTTP_401_UNAUTHORIZED)
            
            token = generate_token(str(user['_id']), user['role'])
            return Response({
                'token': token,
                'user_id': str(user['_id']),
                'role': user['role']
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'username': user['username'],
            'email': user['email'],
            'role': user['role']
        })