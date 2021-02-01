from requests_html import HTMLSession

session = HTMLSession()

# https://www.paris.cl/audifonos-sony-noise-cancelling-wh-1000xm4-negro-424633999.html


def save_price():
    pass


def get_price():
    r = session.get(
        "https://www.paris.cl/audifonos-sony-noise-cancelling-wh-1000xm4-negro-424633999.html"
    )

    price_selector = "#pdpMain > div.row.row-flex.pdp-main-info > div.col-xs-12.col-sm-12.col-md-6.col-lg-5.info-product-detail > div > div.col-xs-12.product-price-2 > div.col-md-6.col-xs-7.price.noPad > div.item-price"
    print(r.html.find(price_selector, first=True).text)


def send_info():
    pass


get_price()
