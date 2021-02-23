import os
from email import message
import smtplib, ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ParisScrapper import get_price

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


def save_price():
    pass


def send_info(receiver, data):
    # password = input("Type passwd: ")

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
    link = "https://www.paris.cl/audifonos-sony-noise-cancelling-wh-1000xm4-negro-424633999.html"
    price = get_price(link)
    send_info(
        "REDACTED", {"name": "Fco Audifonos", "price": price, "link": link}
    )


run()