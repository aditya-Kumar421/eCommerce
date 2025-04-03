from pymongo import MongoClient
from bson import ObjectId, Decimal128
from django.conf import settings
from datetime import datetime

class MongoDBClient:
    _client = None
    _db = None

    @classmethod
    def get_db(cls):
        if cls._client is None:
            cls._client = MongoClient(settings.MONGO_URI)
            cls._db = cls._client[settings.MONGO_DB_NAME]
        return cls._db

class Coupon:
    collection = MongoDBClient.get_db().coupons

    @staticmethod
    def create(data):
        coupon = {
            "_id": str(ObjectId()),
            "code": data["code"],
            "discount_type": data["discount_type"],
            "discount_value": data["discount_value"],
            "expiry_date": data["expiry_date"],
            "usage_limit": data["usage_limit"],
            "used_count": 0,
            "min_order_value": Decimal128(data["min_order_value"]) if data.get("min_order_value") is not None else None
        }
        Coupon.collection.insert_one(coupon)
        return coupon

    @staticmethod
    def get_by_id(coupon_id):
        return Coupon.collection.find_one({"_id": coupon_id})

    @staticmethod
    def get_by_code(code):
        return Coupon.collection.find_one({"code": code})

    @staticmethod
    def get_all():
        return list(Coupon.collection.find())

    @staticmethod
    def update(coupon_id, data):
        if "min_order_value" in data and data["min_order_value"] is not None:
            data["min_order_value"] = Decimal128(data["min_order_value"])
        Coupon.collection.update_one({"_id": coupon_id}, {"$set": data})
        return Coupon.get_by_id(coupon_id)

    @staticmethod
    def increment_used_count(coupon_id):
        Coupon.collection.update_one({"_id": coupon_id}, {"$inc": {"used_count": 1}})
        return Coupon.get_by_id(coupon_id)