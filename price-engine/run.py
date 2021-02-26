import os
import datetime
from typing import Counter

from requests_html import HTMLSession

from database import db
from models import Product, Price
from notificator import send_info


session = HTMLSession()


def parse_price(price_str):
    return int(price_str.split(" ")[0].replace("$", "").replace(".", ""))


def get_price(url):
    r = session.get(url)
    price_selector = "#pdpMain > div.row.row-flex.pdp-main-info > div.col-xs-12.col-sm-12.col-md-6.col-lg-5.info-product-detail > div > div.col-xs-12.product-price-2 > div.col-md-6.col-xs-7.price.noPad > div.item-price"
    return parse_price(r.html.find(price_selector, first=True).text)


def save_price(product_id, price):
    db.collection("products").document(product_id).collection("prices").add(
        price.to_dict()
    )


def compare_last_two_prices(product_id):
    last_price_ref = (
        db.collection("products")
        .document(product_id)
        .collection("prices")
        .order_by("datetime")
        .limit(2)
        .stream()
    )
    try:
        [current_price_doc, last_price_doc] = last_price_ref

        current_price = current_price_doc.to_dict()["number"]
        last_price = last_price_doc.to_dict()["number"]

        variation_decimal_pts = (last_price - current_price) / current_price
        return variation_decimal_pts

    except ValueError:
        print(
            "> (!) there weren't enough saved prices for the product. Variation set to 0 (zero)"
        )
        return 0


def run():
    print("Running...\n")
    product_docs = db.collection("products").stream()
    for product_doc in product_docs:
        if product_doc.exists:
            product = Product.from_dict(product_doc.id, product_doc.to_dict())

            print("Product:", product.name)

            price = get_price(product.url)
            price = Price(price, datetime.datetime.now())
            save_price(product.doc_id, price)

            variation = compare_last_two_prices(product.doc_id)

            if variation != 0:
                print("> (i) notifying the user for price change")
                send_info(
                    "REDACTED",
                    {"name": product.name, "price": price.number, "url": product.url},
                )

            print(f"> (i) price: ${price} ({variation * 100}% since last check)\n")

    print("Finished")


run()