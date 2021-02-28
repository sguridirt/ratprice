import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from models import Product

# Use a service account
cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
firebase_admin.initialize_app(cred)

db = firestore.client()


def create_product(name, url):
    product = Product(None, name, url)
    product_ref = db.collection("products").add(product.to_dict())
    return product_ref
