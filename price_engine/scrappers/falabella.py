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
