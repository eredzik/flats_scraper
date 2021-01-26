from flats_scraper.scrap_otodom_page import scrap_otodom_ad
from httmock import HTTMock, all_requests, urlmatch


@all_requests
def case1(url, request):
    with open('tests/test_src/otodom_test1.html') as f:
        return f.read()


def test_ads_getter():
    with HTTMock(case1):
        results = scrap_otodom_ad(
            "https://www.otodom.pl/oferta/otodom_test1.html")
        assert results is not None
        if results:
            advertisement, user = results
        assert advertisement['floor'] == 2
        assert advertisement['price'] == 515000
        assert user['username'] == 'Michał'
        assert advertisement['build_year'] == 2017
