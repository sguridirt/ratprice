from loguru import logger


def parse_price(price):
    return int(price.replace("$", "").replace(".", "").strip())


def get_price(session, url):
    r = session.get(url)
    price = r.html.xpath("//@data-internet-price", first=True)
    if price:
        return parse_price(price)
    else:
        logger.warning("> (!) price not found.")
        return None


from requests_html import HTMLSession

session = HTMLSession()
get_price(
    session,
    "https://www.falabella.com/falabella-cl/product/14797554/Audifonos-Bluetooth-Noise-Cancelling-WH-1000XM4/14797554",
)
