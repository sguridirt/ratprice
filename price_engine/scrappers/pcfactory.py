from loguru import logger


def parse_price(price):
    return int(price.replace("$", "").replace(".", "").strip())


def get_price(session, url):
    r = session.get(url)
    price_selector = "#id_ficha_producto > div.lp-cuerpo > div.ficha_cuerpo > div > div.ficha_producto_right > div.ficha_producto_precio_wrap > div.ficha_precio_normal > h2"
    price = r.html.find(price_selector, first=True)
    if price:
        return parse_price(price.text)
    else:
        logger.warning("> (!) price not found.")
        return None
