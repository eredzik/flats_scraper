from flats_scraper.get_links import get_ads
from httmock import HTTMock, urlmatch


@urlmatch(netloc=r'(.*\.)?www.olx.pl/nieruchomosci' +
          '/mieszkania/sprzedaz/warszawa/$')
def search_result_mock(url, request):
    with open('tests\\test_src\\search_result.html') as f:
        return f.read()


def test_ads_getter():
    with HTTMock(search_result_mock):
        results = get_ads(pages_to_scrap=1)
    assert sum(["promoted" in x for x in results]) == 0
    assert len(results) == 44
