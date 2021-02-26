import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
firebase_admin.initialize_app(cred)

db = firestore.client()

# # Create user
# user_ref = db.collection("users").add(
#     {"name": "Francisco", "email": "fguridirt@gmail.com"}
# )

# # Check product prices
# product_ref = db.collection("products").document("jE3ZJPLjbSuu66PgPG7K")
# price_docs = product_ref.collection("prices").stream()

# for price in price_docs:
#     print(price)
#     print(f"{price.id} => {price.to_dict()}")
