from pymongo import MongoClient
from bson import ObjectId
from django.conf import settings

class MongoDBClient:
    _client = None
    _db = None

    @classmethod
    def get_db(cls):
        if cls._client is None:
            cls._client = MongoClient(settings.MONGO_URI)
            cls._db = cls._client[settings.MONGO_DB_NAME]
        return cls._db

class Cart:
    collection = MongoDBClient.get_db().carts

    @staticmethod
    def get_by_user_id(user_id):
        return Cart.collection.find_one({"user_id": user_id})

    @staticmethod
    def create(user_id):
        cart = {
            "user_id": user_id,
            "items": [],
            "total_items": 0,
            "total_price": 0.0
        }
        Cart.collection.insert_one(cart)
        return cart

    @staticmethod
    def update(user_id, data):
        Cart.collection.update_one({"user_id": user_id}, {"$set": data}, upsert=True)
        return Cart.get_by_user_id(user_id)

    @staticmethod
    def add_item(user_id, item_data):
        cart = Cart.get_by_user_id(user_id)
        if not cart:
            cart = Cart.create(user_id)
        
        # Check if item already exists
        product_id = item_data["product_id"]
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] += item_data["quantity"]
                break
        else:
            cart["items"].append(item_data)
        
        # Update totals
        cart["total_items"] = sum(item["quantity"] for item in cart["items"])
        cart["total_price"] = sum(item["price"] * item["quantity"] for item in cart["items"])
        
        return Cart.update(user_id, {
            "items": cart["items"],
            "total_items": cart["total_items"],
            "total_price": cart["total_price"]
        })

    @staticmethod
    def remove_item(user_id, product_id):
        cart = Cart.get_by_user_id(user_id)
        if not cart:
            return None
        
        # Remove item
        cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
        
        # Update totals
        cart["total_items"] = sum(item["quantity"] for item in cart["items"])
        cart["total_price"] = sum(item["price"] * item["quantity"] for item in cart["items"])
        
        return Cart.update(user_id, {
            "items": cart["items"],
            "total_items": cart["total_items"],
            "total_price": cart["total_price"]
        })
    
    @staticmethod
    def clear_cart(user_id):
        """Empty the cart after an order is placed."""
        return Cart.update(user_id, {"items": [], "total_items": 0, "total_price": 0.0})