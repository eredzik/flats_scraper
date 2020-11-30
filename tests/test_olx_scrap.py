from httmock import all_requests, HTTMock
from flats_scraper.scrap_olx_page import scrap_olx_ad


def test_ads_getter_1():

    @all_requests
    def mock(url, request):
        with open('tests\\test_src\\olx_test1.html', encoding="utf8") as f:
            return f.read()

    with HTTMock(mock):
        results = scrap_olx_ad('http://www.olx.pl/case1')
        assert results is not None
        if results:
            advertisement, user = results
        assert advertisement['floor'] == 11
        assert advertisement['price'] == 777950
        assert user['username'] == 'Ewa'


def test_ads_getter_2():

    @all_requests
    def mock(url, request):
        with open('tests\\test_src\\olx_test2.html', encoding="utf8") as f:
            return f.read()
    with HTTMock(mock):
        results = scrap_olx_ad('http://www.olx.pl/case1')
        assert results is not None
        if results:
            advertisement, user = results
        assert advertisement['floor'] == 3
        assert advertisement['price'] == 517000
        assert user['username'] == 'Janek'
