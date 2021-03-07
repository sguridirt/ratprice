from notificator.notificator import format_price, format_variation


def test_price_formmating():
    price = 1000000
    formmated_price = format_price(price)
    assert formmated_price == "$1.000.000"


def test_variation_formmating():
    variation = 0.145
    formmated_variation = format_variation(variation)
    assert formmated_variation == "14.5%"
