# -*- coding: utf-8 -*-
import scrapy
from .utils import scrap_from_map, load_json, append_to_dict
import os
import re
from lxml import html
from urllib.parse import urlparse
import json


class OlxOtodomSpider(scrapy.Spider):
    name = 'olx_otodom'
    allowed_domains = ['olx.pl', 'otodom.pl']
    start_urls = ['https://www.olx.pl/nieruchomosci/mieszkania/sprzedaz/warszawa/']
    path = os.path.dirname(os.path.realpath(__file__))
    site_map = load_json(os.path.join(path, 'site_map_main.json'))
    olx_map = load_json(os.path.join(path, 'site_map_olx.json'))
    otodom_map = load_json(os.path.join(path, 'site_map_otodom.json'))
    max_sites = 1
    yielded_sites = 0

    def parse(self, response):
        hxs = html.fromstring(response.text)
        if self.yielded_sites < self.max_sites:
            result = scrap_from_map(hxs, self.site_map)
            self.yielded_sites += 1
            for url in result['ads']:
                parsed_url = urlparse(url)
                # print(parsed_url)
                if parsed_url.netloc == 'www.olx.pl':
                    # pass
                    yield scrapy.Request(url=url, callback=self.parse_olx)
                elif parsed_url.netloc == 'www.otodom.pl':
                    yield scrapy.Request(url, callback=self.parse_otodom)
                else:
                    raise KeyError
            response = scrapy.Request(url=result['nextPage'], callback=self.parse)
            response.meta['dont_cache'] = True
            yield response

    def parse_olx(self, response):
        hxs = html.fromstring(response.text)
        result = scrap_from_map(hxs, self.olx_map)
        result['url'] = response.url
        append_to_dict(result,
                       dict(zip(result['tableKeys'],
                                result['tableValues'])))
        del result['tableValues']
        del result['tableKeys']
        stmp = result.copy()
        processed_data = dict()

        processed_data['posted_by'] = stmp.get('Oferta od')
        processed_data['level'] = stmp.get('Poziom')
        processed_data['decorated'] = stmp.get('Umeblowane')
        processed_data['market'] = stmp.get('Rynek')
        processed_data['type_of_building'] = stmp.get('Rodzaj zabudowy')
        processed_data['no_rooms'] = re.findall("[0-9]+",
                                                stmp.get('Liczba pokoi'))[0]
        processed_data['size_sqmeters'] = re.findall('[0-9]+',
                                                     stmp.get('Powierzchnia')
                                                     .replace(',', '.'))[0]
        processed_data['description'] = stmp.get('description').strip()
        # string_json = re.findall("{.*}", str(stmp['phone_number']))
        # if not string_json:
        #     self.processed_data['phone_number'] = "None"
        # else:
        #     self.processed_data['phone_number'] = json.loads(string_json[0].replace("'", "\""))['id_raw']
        processed_data['price'] = stmp.get('price').replace(' ', '').replace('zł', '')
        processed_data['id'] = re.findall("[0-9]+", stmp.get('id'))[0]
        append_to_dict(processed_data, {k: stmp[k] for k in
                                        ['location', 'views', 'latitude', 'longitude', 'url']})
        #print(processed_data['id'])
        # if processed_data['id'] == '547131834':
        #     print("TU")
        #     raise KeyError
        #     pass
        yield processed_data

    def parse_otodom(self, response):

        processed_data = dict()
        hxs = html.fromstring(response.text)
        result = scrap_from_map(hxs, self.otodom_map)
        result['url'] = response.url
        append_to_dict(result,
                       dict(zip(result['tableKeys'],
                                result['tableValues'])))
        del result['tableValues']
        del result['tableKeys']
        result1 = json.loads(result.get('json_script'))
        processed_data['price'] = result1['@graph'][1]['price']
        processed_data['latitude'] = result1['@graph'][0]['geo']['latitude']
        processed_data['longitude'] = result1['@graph'][0]['geo']['longitude']
        processed_data['location'] = result1['@graph'][0]['address']['streetAddress']
        processed_data['description'] = result1['@graph'][0]['description']\
            .replace('\n', '')\
            .replace('\t', '')\
            .replace('\r', '')
        processed_data['id'] = re.findall("[0-9]+", result.get('id'))[0]
        processed_data['size_sqmeters'] = re.findall('[0-9]+',
                                                     result.get('Powierzchnia: ')
                                                     .replace(',', '.'))[0]
        processed_data['no_rooms'] = result.get('Liczba pokoi: ')
        processed_data['type_of_building'] = result.get('Rodzaj zabudowy: ')
        processed_data['market'] = result.get('Rynek: ')
        processed_data['level'] = result.get('Piętro: ')
        processed_data['decorated'] = result.get('Stan wykończenia: ')
        append_to_dict(processed_data, {k: result[k] for k in
                                        ['url']})

        yield processed_data

