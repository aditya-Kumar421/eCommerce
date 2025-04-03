from pymongo import MongoClient
from bson import ObjectId
import os
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from decouple import config
# MongoDB connection
from django.conf import settings
db_client = MongoClient(settings.MONGO_URI)
db = db_client["eCommerce"]

class Category:
    collection = db['categories']
    
    @staticmethod
    def create(data):
        return Category.collection.insert_one(data).inserted_id
    
    @staticmethod
    def get_all():
        return list(Category.collection.find())
    
    @staticmethod
    def get_by_id(category_id):
        return Category.collection.find_one({'_id': ObjectId(category_id)})
    
    @staticmethod
    def update(category_id, data):
        return Category.collection.update_one(
            {'_id': ObjectId(category_id)},
            {'$set': data}
        ).modified_count
    
    @staticmethod
    def delete(category_id):
        return Category.collection.delete_one({'_id': ObjectId(category_id)}).deleted_count

class Product:
    collection = db['products']
    
    @staticmethod
    def create(data, image_file=None):
        if image_file:
            # Upload to Cloudinary
            upload_result = upload(image_file)
            data['image_url'] = upload_result['secure_url']
        
        return Product.collection.insert_one(data).inserted_id
    
    @staticmethod
    def get_all():
        return list(Product.collection.find())
    
    @staticmethod
    def get_by_id(product_id):
        try:
            product = db.products.find_one({"_id": ObjectId(product_id)})
            return product  # Returns dict or None
        except:
            return None 
    
    @staticmethod
    def update(product_id, data, image_file=None):
        if image_file:
            upload_result = upload(image_file)
            data['image_url'] = upload_result['secure_url']
        
        return Product.collection.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': data}
        ).modified_count
    
    @staticmethod
    def delete(product_id):
        return Product.collection.delete_one({'_id': ObjectId(product_id)}).deleted_count