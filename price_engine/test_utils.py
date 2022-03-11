from utils import get_product_site


def test_extract_url_site():
    site = get_product_site("https://example.com/")
    assert site == "example.com"
