from loguru import logger


def parse_price(price_str):
    return int(price_str.split(" ")[0].replace("$", "").replace(".", ""))


def get_price(session, url):
    r = session.get(url)
    price_selector = "#pdpMain > div.row.row-flex.pdp-main-info > div.col-xs-12.col-sm-12.col-md-6.col-lg-5.info-product-detail > div > div.col-xs-12.product-price-2 > div.col-md-6.col-xs-7.price.noPad > div.item-price"
    price = r.html.find(price_selector, first=True)
    if price:
        return parse_price(price.text)
    else:
        logger.warning("> (!) price not found.")
        return None