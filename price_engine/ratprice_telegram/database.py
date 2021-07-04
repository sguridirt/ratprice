import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

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
