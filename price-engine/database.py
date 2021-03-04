import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from models import Product

cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
firebase_admin.initialize_app(cred)

db = firestore.client()


def create_product(name, url):
    product = Product(None, name, url)
    product_ref = db.collection("products").add(product.to_dict())
    return product_ref


def user_track_product(user_id, product_id):
    user_ref = db.collections("users").document(user_id)
    product_ref = db.collections("products").document(product_id)

    user_product_ref = db.collections("userProducts").add(
        {"productId": product_ref, "userId": user_ref}
    )
    return user_product_ref


def copy_collection(source_collection_name, new_collection_name):
    collection_docs = db.collection(source_collection_name).stream()

    for doc in collection_docs:
        print(doc)
        db.collection(new_collection_name).add(doc.to_dict())
