import os

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from jinja2 import Environment, FileSystemLoader
from jinja2.environment import Template

port = 465
context = ssl.create_default_context()

env = Environment(
    loader=FileSystemLoader("{0}/templates/".format(os.path.dirname(__file__)))
)

text = """\
Hi!
{0}'s current price is: ${1} ({3}%% since last check)
Your product url: {2}

Enjoy!
ratprice."""

html = """\
<html>
    <body>
        <p>🐭💰</p>
        <p><a href="{2}">{0}</a>'s current price is: $<b>{1}</b> ({3}%% since last check)</p>
    </body>
</html>"""


def format_price(price):
    """Takes the price as an integer and returns it as a formatted string. (123000 -> $123.000)

    Args:
        price (int): the price as an integer.

    Returns:
        str: the formatted price as a string.
    """
    return "${:,}".format(price).replace(",", ".")


def format_variation(variation):
    return "{:.1%}".format(variation)


def load_template(data):
    template = env.get_template("template.html")
    output = template.render(data=data)
    return output


def send_mail(receiver, data):
    sender = "ratprice. <ratpricemsg@gmail.com>"

    message = MIMEMultipart("alternative")
    message["Subject"] = f"🙌 {data['product_name']} price: ${data['price']}"
    message["From"] = sender
    message["To"] = receiver

    data["price"] = format_price(data["price"])
    data["variation"] = format_variation(data["variation"])

    message.attach(
        MIMEText(
            text.format(
                data["product_name"], data["price"], data["url"], data["variation"]
            ),
            "plain",
        )
    )

    html_content = load_template(data)

    message.attach(
        MIMEText(
            html_content,
            "html",
        )
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("ratpricemsg@gmail.com", os.environ["PASSWD"])
        server.sendmail(sender, receiver, message.as_string())