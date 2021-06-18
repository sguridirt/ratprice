import tldextract


def get_product_site(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"
