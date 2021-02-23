from requests_html import HTMLSession

session = HTMLSession()


def get_price(url):
    r = session.get(url)
    price_selector = "#pdpMain > div.row.row-flex.pdp-main-info > div.col-xs-12.col-sm-12.col-md-6.col-lg-5.info-product-detail > div > div.col-xs-12.product-price-2 > div.col-md-6.col-xs-7.price.noPad > div.item-price"
    return r.html.find(price_selector, first=True).text.split(" ")[0].replace("$", "")
