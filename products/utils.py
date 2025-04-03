import cloudinary.uploader
from django.conf import settings
from rest_framework.permissions import BasePermission

def upload_to_cloudinary(image_file):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY['cloud_name'],
        api_key=settings.CLOUDINARY['api_key'],
        api_secret=settings.CLOUDINARY['api_secret']
    )
    upload_result = cloudinary.uploader.upload(image_file)
    return upload_result['secure_url']

class IsAuthenticatedCustom(BasePermission):
    """
    Custom permission to allow access only to authenticated users.
    Checks if request.user is a non-empty dictionary (MongoDB user document).
    """
    def has_permission(self, request, view):
        return bool(request.user and isinstance(request.user, dict))

class IsAdminUser(BasePermission):
    """
    Custom permission to allow access only to admin users.
    Checks if request.user has 'role' == 'admin'.
    """
    def has_permission(self, request, view):
        return bool(request.user and isinstance(request.user, dict) and request.user.get('role') == 'admin')