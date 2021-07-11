import os
import datetime

from firebase_admin import firestore
from loguru import logger
from requests_html import HTMLSession

from database import db
from models import Product, Price, User
from scrappers import paris, falabella, ripley, pcfactory
from utils import get_product_site
from ratprice_telegram import alert


def get_price(session, url):
    if "falabella.com" in url:
        return falabella.get_price(session, url)
    elif "paris.cl" in url:
        return paris.get_price(session, url)
    elif "ripley.cl" in url:
        return ripley.get_price(session, url)
    elif "pcfactory.cl" in url:
        return pcfactory.get_price(session, url)


def save_price(product_id, price):
    db.collection("products").document(product_id).collection("prices").add(
        price.to_dict()
    )


def compare_last_two_prices(product_id):
    last_price_ref = (
        db.collection("products")
        .document(product_id)
        .collection("prices")
        .order_by("datetime", direction=firestore.Query.DESCENDING)
        .limit(2)
        .stream()
    )
    try:
        [current_price_doc, last_price_doc] = last_price_ref
        current_price = current_price_doc.to_dict()["number"]
        last_price = last_price_doc.to_dict()["number"]
        variation_decimal_pts = (current_price - last_price) / last_price
        return variation_decimal_pts, last_price

    except ValueError:
        logger.info(
            "> (!) there weren't saved prices for the product. Variation set to `0`"
        )
        return 0, 0


def get_users_tracking_product(product_ref):
    tracked_product_docs = (
        db.collection("userProducts").where("productId", "==", product_ref).stream()
    )

    for doc in tracked_product_docs:
        user_id = doc.to_dict()["userId"].get().id
        user_data = db.collection("users").document(user_id).get().to_dict()
        user = User(user_data["name"], user_data["email"], user_data["telegramId"])
        yield user


def run():
    logger.info("Running...")

    session = HTMLSession()
    product_docs = db.collection("products").stream()
    for product_doc in product_docs:
        if product_doc.exists:
            product = Product.from_dict(product_doc.id, product_doc.to_dict())
            product_ref = db.collection("products").document(product.doc_id)

            logger.info(f"Product: {product.name}")

            price = get_price(session, product.url)
            if price:
                price = Price(price, datetime.datetime.now(datetime.timezone.utc))
                save_price(product.doc_id, price)

                variation, old_price_number = compare_last_two_prices(product.doc_id)

                if variation < 0:
                    logger.info("> (i) notifying the user for price change")

                    users_tracking_product = get_users_tracking_product(product_ref)
                    for user in users_tracking_product:
                        alert(
                            user.telegramId,
                            {
                                "product_name": product.name,
                                "price": price.number,
                                "old_price": old_price_number,
                                "variation": variation,
                                "url": product.url,
                                "site": get_product_site(product.url),
                            },
                        )

                logger.info(
                    f"> (i) price: ${price} ({variation * 100}% since last check)"
                )
            else:
                logger.warning(f"> (!) price not detected for {product.name}")

    logger.success("Finished")


run()