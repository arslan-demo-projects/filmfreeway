import re
from html import unescape

import usaddress


def clean(text):
    text = re.sub(u'"', u"\u201C", unescape(text or ''))
    text = re.sub(u"'", u"\u2018", text)
    for c in ['\r\n', '\n\r', u'\n', u'\r', u'\t', u'\xa0']:
        text = text.replace(c, ' ')
    return re.sub(' +', ' ', text).strip()


def get_address_parts(address):
    address1, city, state, zip_code = '', '', '', ''

    for value, key in usaddress.parse(address):
        value = value.replace(',', '') + ' '
        if key in ['OccupancyIdentifier', 'Recipient']:
            continue
        if key == 'PlaceName':
            city += value
        elif key == 'StateName':
            state += value
        elif key == 'ZipCode':
            zip_code += value
        else:
            address1 += value

    address_item = dict(
        address1=clean(address1),
        city=clean(city),
        state=state.strip().upper(),
        zip=zip_code[:5].strip(),
    )
    return address_item
