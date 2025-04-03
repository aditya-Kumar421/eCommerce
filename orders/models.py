from pymongo import MongoClient
from bson import ObjectId
from django.conf import settings
from datetime import datetime
from cart.models import Cart  # Assuming Cart is defined in carts/models.py
from coupons.models import Coupon  # Assuming Coupon is defined in coupons/models.py
class MongoDBClient:
    _client = None
    _db = None

    @classmethod
    def get_db(cls):
        if cls._client is None:
            cls._client = MongoClient(settings.MONGO_URI)
            cls._db = cls._client[settings.MONGO_DB_NAME]
        return cls._db


class Order:
    collection = MongoDBClient.get_db().orders

    @staticmethod
    def create(user_id, cart, coupon_id=None, discount_applied=0.0):
        total_amount = cart["total_price"]
        final_amount = total_amount - discount_applied
        order = {
            "_id": str(ObjectId()),
            "user_id": user_id,
            "items": cart["items"],
            "total_amount": total_amount,
            "discount_applied": discount_applied,
            "final_amount": final_amount,
            "coupon_id": coupon_id,
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        Order.collection.insert_one(order)
        if coupon_id:
            from coupons.models import Coupon
            Coupon.increment_used_count(coupon_id)  # Increment usage
        Cart.clear_cart(user_id)
        return order

    @staticmethod
    def get_by_id(order_id):
        return Order.collection.find_one({"_id": order_id})

    @staticmethod
    def get_by_user_id(user_id):
        return list(Order.collection.find({"user_id": user_id}))

    @staticmethod
    def update_status(order_id, status):
        valid_statuses = ["pending", "shipped", "delivered"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        Order.collection.update_one({"_id": order_id}, {"$set": {"status": status}})
        return Order.get_by_id(order_id)