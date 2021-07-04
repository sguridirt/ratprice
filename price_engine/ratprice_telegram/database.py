import os

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.document import DocumentReference

cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
firebase_admin.initialize_app(cred)

db = firestore.client()


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
        new_product_ref = db.collection("products").add({"name": name, "URL": url})

        db.collection("userProducts").add(
            {
                "productId": DocumentReference(
                    "products", new_product_ref[1].id, client=db
                ),
                "userId": DocumentReference("users", user.id, client=db),
            }
        )
