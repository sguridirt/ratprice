import re

from loguru import logger


def parse_price(price_str):
    price = re.sub("[^0-9]", "", price_str)
    return int(price)


def get_price(session, url):
    r = session.get(url)
    price_container_selector = "//*[@id='row']/div[2]/section[2]/dl/div"
    price = r.html.xpath(price_container_selector, first=True)
    if price:
        return parse_price(price.text)
    else:
        logger.warning("> (!) price not found.")
        return None
