import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.document import DocumentReference

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


def save_user(telegram_id, name):
    db.collection("users").add({"telegramId": telegram_id, "name": name})


def fetch_user(telegram_id):
    user_ref = db.collection("users").where("telegramId", "==", telegram_id).limit(1)
    try:
        return user_ref.get()[0]
    except IndexError:
        return None


def save_product(name, url, telegram_id):
    user = fetch_user(telegram_id)
    if user:
        # Check if product already exists
        product_ref = (
            db.collection("products").where("URL", "==", url).limit(1).get()[0]
        )
        product_doc = product_ref.get()[0]

        if not product_doc.exists:
            product_ref = db.collection("products").add({"name": name, "URL": url})

        # Link user and new product
        db.collection("userProducts").add(
            {
                "productId": DocumentReference(
                    "products", product_ref[1].id, client=db
                ),
                "userId": DocumentReference("users", user.id, client=db),
            }
        )


def get_user_products(user_id):
    user_id = DocumentReference("users", user_id, client=db)

    userProduct_stream = (
        db.collection("userProducts").where("userId", "==", user_id).stream()
    )
    for userProduct in userProduct_stream:
        product_ref = userProduct.get("productId")
        yield product_ref.get()


def get_last_price(product_id):
    last_price_ref = (
        db.collection("products")
        .document(product_id)
        .collection("prices")
        .order_by("datetime", direction=firestore.Query.DESCENDING)
        .limit(1)
        .get()
    )

    return last_price_ref[0].to_dict()["number"]
