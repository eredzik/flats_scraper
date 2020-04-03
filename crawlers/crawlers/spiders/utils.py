import json

import lxml.etree


class Error(Exception):
    pass


def table_iterate(html_table):
    pass


def load_json(json_file):
    with open(json_file) as f:
        return json.loads(f.read())


def save_json(filename, dictionary_to_save):
    with open(filename, 'w', encoding='utf8') as json_file:
        json.dump(dictionary_to_save, json_file, indent=2, ensure_ascii=False)


def save_list(filename, list_to_save):
    with open(filename, "w") as f:
        for elem in list_to_save:
            f.write(elem + '\n')


def load_list(filename, searchstring=''):
    link_set = set()
    with open(filename, 'r') as f:
        for line in f:
            if (searchstring in line) or searchstring is '':
                link_set.add(line.rstrip('\n'))
    return link_set


def scrap_from_map(site, mapping):
    scraped_data = {}
    found = None
    for map_id, map_keys in mapping.items():
        try:
            if map_keys['attrib'] == 'value':
                found = [str(content.text).replace('\n', '').replace('\t', '').replace('\r', '')
                         if map_keys.get('method') == 'text'
                         else str(content.text_content()).replace('\n', '').replace('\t', '').replace('\r', '')
                         for content in site.xpath(map_keys['xpath'])]
            else:
                found = [str(content.get(map_keys['attrib'])).replace('\n', '').replace('\t', '').replace('\r', '')
                         for content in site.xpath(map_keys['xpath'])]
        except lxml.etree.XPathEvalError:
            print("Error in {} : {}".format(map_id, map_keys['xpath']))
        if len(found) == 1:
            found = found[0]
        scraped_data[map_id] = found
    return scraped_data


def append_to_dict(original_dict, new_dict):
    for key in new_dict.keys():
        if key not in original_dict.keys():
            original_dict[key] = new_dict[key]
# open_link_file('site_links20190729-160003')


# print(import_map(r'C:\Projekty\MieszkaniaScraping\mieszkania_v2\olx_starting_point_map.csv'))
