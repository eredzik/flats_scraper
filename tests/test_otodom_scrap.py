from httmock import urlmatch, HTTMock
from flats_scraper.scrap_otodom_page import scrap_otodom_ad


@urlmatch(netloc=r'(.*\.)?www.otodom.pl/oferta(.*)$')
def case1(url, request):
    with open('tests\\test_src\\otodom_test1.html') as f:
        return f.read()


def test_ads_getter():
    with HTTMock(case1):
        results = scrap_otodom_ad(
            "https://www.otodom.pl/oferta/" +
            "pole-mokotowskie-sgh-metro-kamienica-cicho-2-8h-ID47Z2V.html")
        assert results is not None
        if results:
            advertisement, user = results
        assert advertisement['floor'] == 1
        assert advertisement['price'] == 790000
        assert user['username'] == 'Joanna Myśkiewicz'
        assert advertisement['build_year'] == 1950
