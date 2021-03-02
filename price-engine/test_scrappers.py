import pytest
from scrappers import falabella, paris, pcfactory, ripley

from requests_html import HTMLSession


@pytest.fixture(scope="module")
def session():
    """Returns an HTMLSession from requests_html"""
    return HTMLSession()


def test_falabella_price(session):
    price = falabella.get_price(
        session,
        "https://www.falabella.com/falabella-cl/product/14797554/Audifonos-Bluetooth-Noise-Cancelling-WH-1000XM4/14797554",
    )
    assert type(price) is int


def test_paris_price(session):
    price = paris.get_price(
        session,
        "https://www.paris.cl/audifonos-sony-noise-cancelling-wh-1000xm4-negro-424633999.html",
    )
    assert type(price) is int


def test_pcfactory_price(session):
    price = pcfactory.get_price(
        session,
        "https://www.pcfactory.cl/producto/38714-sony-audifono-bluetooth-noise-cancelling-1000xm4",
    )
    assert type(price) is int


def test_ripley_price(session):
    price = ripley.get_price(
        session,
        "https://simple.ripley.cl/audifonos-sony-wh-1000xm3-2000373897021p?s=o",
    )
    assert type(price) is int