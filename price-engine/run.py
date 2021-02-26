import os
import datetime
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from requests_html import HTMLSession

from database import db


session = HTMLSession()


def get_price(url):
    r = session.get(url)
    price_selector = "#pdpMain > div.row.row-flex.pdp-main-info > div.col-xs-12.col-sm-12.col-md-6.col-lg-5.info-product-detail > div > div.col-xs-12.product-price-2 > div.col-md-6.col-xs-7.price.noPad > div.item-price"
    return r.html.find(price_selector, first=True).text.split(" ")[0].replace("$", "")


def parse_price(price_str):
    return int(price_str.replace(".", ""))


def save_price(product_id, price):
    db.collection("products").document("{0}".format(product_id)).collection(
        "prices"
    ).add(
        {
            "number": parse_price(price),
            "udatetime": datetime.datetime.now(),
        }
    )


port = 465
context = ssl.create_default_context()
sender = "ratprice. <ratpricemsg@gmail.com>"


text = """\
Hi!
{0}'s current price is: ${1}.
Your product link: {2}

Enjoy!
ratprice."""

html = """\
<html>
    <body>
        <p>💰🐭💰</p>
        <p><a href="{2}">{0}</a>'s current price is: $<b>{1}</b></p>
    </body>
</html>"""


def send_info(receiver, data):

    message = MIMEMultipart("alternative")
    message["Subject"] = f"{data['name']} price: ${data['price']}"
    message["From"] = sender
    message["To"] = receiver

    message.attach(
        MIMEText(text.format(data["name"], data["price"], data["link"]), "plain")
    )
    message.attach(
        MIMEText(html.format(data["name"], data["price"], data["link"]), "html")
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("ratpricemsg@gmail.com", os.environ["PASSWD"])
        server.sendmail(sender, receiver, message.as_string())


def run():
    print("Running...")
    product_docs = db.collection("products").stream()
    for product_doc in product_docs:
        if product_doc.exists:
            product = product_doc.to_dict()
            price = get_price(product["URL"])
            save_price(product_doc.id, price)
            send_info(
                "sguridirt@gmail.com",
                {"name": product["name"], "price": price, "link": product["URL"]},
            )
    print("Finished")


run()