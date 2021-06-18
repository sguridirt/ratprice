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
    user_ref = db.collection("users").document(user_id)
    product_ref = db.collection("products").document(product_id)

    user_product_ref = db.collection("userProducts").add(
        {"productId": product_ref, "userId": user_ref}
    )
    return user_product_ref


def add_field_collection_docs(field_path, field_value, collection_name):
    """Adds a new field to every document in collection.

    Args:
        field_path (str): field name or path (eg. 'field_name' or 'field.nested_field_name')
        field_value (Firestore supported value type): field value
        collection_name (str): collection name in which documents to be updated reside
    """
    collection_docs = db.collection(collection_name).stream()
    for doc in collection_docs:
        if doc.exists:
            db.collection(collection_name).document(doc.id).update(
                {field_path: field_value}
            )


def copy_collection(source_collection_name, new_collection_name):
    collection_docs = db.collection(source_collection_name).stream()

    for doc in collection_docs:
        print(doc)
        db.collection(new_collection_name).add(doc.to_dict())
