import os
from typing import Any, Iterator, Optional, Tuple
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.document import DocumentReference

from models import Product

cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
firebase_admin.initialize_app(cred)

db = firestore.client()


def create_product(name: str, url: str) -> DocumentReference:
    product = Product(None, name, url)
    product_ref = db.collection("products").add(product.to_dict())
    return product_ref


def user_track_product(user_id: str, product_id: str) -> DocumentReference:
    user_ref = db.collection("users").document(user_id)
    product_ref = db.collection("products").document(product_id)

    user_product_ref = db.collection("userProducts").add(
        {"productId": product_ref, "userId": user_ref}
    )
    return user_product_ref


def user_untrack_product(user_id: str, product_id: str) -> dict[str, bool]:
    user_id = DocumentReference("users", user_id, client=db)
    product_id = DocumentReference("products", product_id, client=db)

    user_product = (
        db.collection("userProducts")
        .where("userId", "==", user_id)
        .where("productId", "==", product_id)
        .limit(1)
        .get()
    )

    try:
        user_product[0].reference.delete()
        return {"success": True}
    except IndexError:
        return {"success": False}


def add_field_collection_docs(field_path: str, field_value: Any, collection_name: str):
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


def copy_collection(source_collection_name: str, new_collection_name: str):
    collection_docs = db.collection(source_collection_name).stream()

    for doc in collection_docs:
        print(doc)
        db.collection(new_collection_name).add(doc.to_dict())


def save_user(telegram_id: int, name: str):
    db.collection("users").add({"telegramId": telegram_id, "name": name})


def fetch_user(telegram_id: int) -> Optional[DocumentReference]:
    user_ref = db.collection("users").where("telegramId", "==", telegram_id).limit(1)
    try:
        return user_ref.get()[0]
    except IndexError:
        return None


def save_product(name: str, url: str, telegram_id: int) -> DocumentReference:
    user = fetch_user(telegram_id)
    if user:
        # Check if product already exists
        try:
            product_doc = (
                db.collection("products").where("URL", "==", url).limit(1).get()[0]
            )
            product_ref = product_doc.reference
        except IndexError:
            product_ref = db.collection("products").add({"name": name, "URL": url})[1]

        # Link user and new product
        _, new_product_ref = db.collection("userProducts").add(
            {
                "productId": DocumentReference("products", product_ref.id, client=db),
                "userId": DocumentReference("users", user.id, client=db),
            }
        )
        return new_product_ref


def get_user_products(user_id: str) -> Iterator[DocumentReference]:
    user_id = DocumentReference("users", user_id, client=db)

    user_product_stream = (
        db.collection("userProducts").where("userId", "==", user_id).stream()
    )
    for userProduct in user_product_stream:
        product_ref = userProduct.get("productId")
        yield product_ref.get()


def get_last_price(product_id: str) -> Tuple[Optional[int], Optional[datetime]]:
    last_price_ref = (
        db.collection("products")
        .document(product_id)
        .collection("prices")
        .order_by("datetime", direction=firestore.Query.DESCENDING)
        .limit(1)
        .get()
    )

    try:
        last_price = last_price_ref[0].to_dict()
        return last_price["number"], last_price["datetime"]
    except IndexError:
        return None, None
