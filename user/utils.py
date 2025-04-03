import jwt
from datetime import datetime, timedelta,timezone
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from pymongo import MongoClient
from decouple import config
from bson.objectid import ObjectId

SECRET_KEY = config('SECRET_KEY')  # Change this in production

def generate_token(user_id, role):
    payload = {
        'user_id': str(user_id),  # Ensure user_id is stored as string in token
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(days=1),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            token = auth_header.split('Bearer ')[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            # print(f"Token payload: {payload}")
            
            client = MongoClient(settings.MONGO_URI)
            db = client[settings.MONGO_DB_NAME]
            
            try:
                user_id = ObjectId(payload['user_id'])
            except Exception as e:
                # print(f"Invalid user_id format: {e}")
                raise AuthenticationFailed('Invalid user_id in token')
                
            # print(f"Querying user with _id: {user_id}")
            user = db.users.find_one({'_id': user_id})
            
            if not user:
                # print("User not found in database")
                raise AuthenticationFailed('User not found')
            user['_id'] = str(user['_id'])
            # print(f"Found user: {user}")
            return (user, token)
        except (IndexError, jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            # print(f"Authentication error: {str(e)}")
            raise AuthenticationFailed('Invalid token')