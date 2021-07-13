from scrappers import falabella, paris, pcfactory, ripley

REGISTERED_SCRAPPERS = ["falabella.com", "paris.cl", "ripley.cl", "pcfactory.cl"]


def get_price(session, url):
    if "falabella.com" in url:
        return falabella.get_price(session, url)
    elif "paris.cl" in url:
        return paris.get_price(session, url)
    elif "ripley.cl" in url:
        return ripley.get_price(session, url)
    elif "pcfactory.cl" in url:
        return pcfactory.get_price(session, url)