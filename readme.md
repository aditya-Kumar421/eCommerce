# 🛒 eCommerce Backend API

This is a robust and scalable **eCommerce backend** built using **Django Rest Framework (DRF)** and **MongoDB**. It provides a full-featured API for managing products, carts, orders, and user authentication. The application is optimized using Redis for product management and Celery for background tasks. It also includes support for coupon codes and is deployed on AWS.

---

## 🚀 Features

- 🔐 **JWT Authentication** (Register, Login, Profile, Logout)
- 📦 **Product Management** with Redis caching
- 🛍️ **Cart Functionality**
- 📑 **Order System** with:
  - Coupon code support
  - Order status tracking
- ✉️ **Background Email Notifications** (on order status updates) via Celery
- ☁️ **AWS Hosting**
- 📡 **MongoDB** as the primary database (via PyMongo)
- ⚡ **Redis** for fast product lookups and caching

---

## 🧰 Tech Stack

| Category          | Tech                                |
|-------------------|-------------------------------------|
| Backend Framework | Django Rest Framework (DRF)         |
| Database          | MongoDB (PyMongo)                   |
| Caching           | Redis                               |
| Task Queue        | Celery + Redis (as broker)          |
| Authentication    | JWT (djangorestframework-simplejwt) |
| Hosting           | AWS EC2 / AWS Services              |
| Background Tasks  | Celery                              |

---
<h2>🚀 Documentation</h2>

[Postman-documentation](https://documenter.getpostman.com/view/41200302/2sB2cU9MwS)

  
<h2>🛠️ Installation Steps:</h2>

1. Clone the repository:

```CMD
git clone https://github.com/aditya-Kumar421/eCommerce.git
```

To run the server, you need to have Python installed on your machine. If you don't have it installed, you can follow the instructions [here](https://www.geeksforgeeks.org/download-and-install-python-3-latest-version/) to install it.

2. Install and Create a virtual environment:

```CMD
python -m venv env
```

3. Activate the virtual environment

```CMD
env\Scripts\activate
cd eCommerce
```

4. Install the dependencies:

```CMD
pip install -r requirements.txt
```

5. Set Up Database:

```
python manage.py migrate
```

6. Run the Development Server:

```
python manage.py runserver
```

7. Access the Endpoints:

```
Use Postman to test functions.
```
