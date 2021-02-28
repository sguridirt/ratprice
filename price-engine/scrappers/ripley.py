import re
from requests_html import HTMLSession

session = HTMLSession()


def parse_price(price_str):
    price = re.sub("[^0-9]", "", price_str)
    return int(price)


def get_price(url):
    r = session.get(url)
    price_container_selector = "//*[@id='row']/div[2]/section[2]/dl/div"
    return parse_price(r.html.xpath(price_container_selector, first=True).text)
