from loguru import logger


def parse_price(price):
    return int(price.replace("$", "").replace(".", "").strip())


def get_price(session, url):
    r = session.get(url)
    price_selector = "/html/body/div[1]/div/section/div[1]/div[1]/div[2]/section[2]/div[2]/div/div[2]/div[1]/div[1]/ol/li[1]/div/span"
    price = r.html.xpath(price_selector, first=True)
    if price:
        return parse_price(price.text)
    else:
        logger.warning("> (!) price not found.")
        return None
