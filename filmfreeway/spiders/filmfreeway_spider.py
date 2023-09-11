# -*- coding: utf-8 -*-

import time
from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
from urllib.parse import urljoin, quote_plus

from scrapy import Spider, Request, signals
from scrapy.crawler import CrawlerProcess

from gs_automation import GoogleSheetAutomation
from utils import clean, get_address_parts


class FilmFreeWaySpider(Spider, GoogleSheetAutomation):
    name = 'filmfreeway-spider'
    file_name = "../output/film_festivals.csv"
    base_url = 'https://filmfreeway.com/festivals'
    search_url_t = urljoin(base_url, "?ga_search_category=Festival&q={q}&fees_currency=USD&years=1%3B50&sort=relevance")

    handle_httpstatus_list = [
        400, 401, 402, 403, 404, 405, 406, 407, 409,
        500, 501, 502, 503, 504, 505, 506, 507, 509,
    ]

    csv_columns = [
        'FilmFestivalID', 'FilmFestivalName', 'FilmFestivalNameOfficial',
        'FilmFestivalWebsite', 'FilmFestivalLevel', 'FilmFestivalDeadlineMonth',
        'FilmFestivalFilmAge', 'FilmFestivalFilmLenght', 'FilmFestivalGenre01',
        'FilmFestivalGenre02', 'FilmFestivalGenre03', 'FilmFestivalCountry', 'FilmFestivalCity',
        'FilmFestivalPremiereRequirement', 'FilmFestivalAcademyCredited', 'FilmFestivalEFACredited',
        'FilmFestivalBaftaCredited', 'FilmFestivalFIAPFcredited', 'FilmFestivalCanadianSCredited',
        'FilmFestivalGoyaCredited', 'FilmFestivalAbout', 'FilmFestivalAddress', 'FilmFestivalCategories',
        'FilmFestivalDeadlineEarly', 'FilmFestivalDeadlineRegular', 'FilmFestivalDeadlineLate',
        'FilmFestivalDeadlineExtended', 'FilmFestivalEmailGeneral', 'FilmFestivalFacebookPage',
        'FilmFestivalInstagramPage', 'FilmFestivalTwitter', 'FilmFestivalOtherSocialMedia',
        'FilmFestivalFirstEditionYear', 'FilmFestivalOrganizers', 'FilmFestivalRulesTerms',
        'FilmFestivalFilmfreewayLink', 'FilmFestivalTelephone', 'FilmFestivalVenue01',
        'FilmFestivalVenue02', 'FilmFestivalVenue03', 'FilmFestivalVenue04', 'FilmFestivalVenue05',
        'FilmFestivalVenue06', 'FilmFestivalVenue07', 'FilmFestivalFeeEarlyUSD',
        'FilmFestivalFeeRegularUSD', 'FilmFestivalFeeLateUSD', 'FilmFestivalFeeEarlyEUR',
        'FilmFestivalFeeRegularEUR', 'FilmFestivalFeeLateEUR', 'FilmFestivalDirector',
        'FilmFestivalArtisticDirector', 'FilmFestivalSeniorProgrammer01', 'FilmFestivalSeniorProgrammer02',
        'FilmFestivalSeniorProgrammer03', 'FilmFestivalShortsProgrammer01', 'FilmFestivalShortsProgrammer02',
        'FilmFestivalRoleOther01', 'FilmFestivalRoleOther02', 'FilmFestivalRoleOther03',
        'FilmFestivalAwards01', 'FilmFestivalAwards02', 'FilmFestivalAwards03', 'FilmFestivalAwards04',
        'FilmFestivalAwards05', 'FilmFestivalAwards06', 'FilmFestivalAwards07'
    ]

    currencies = [
        '£', '¥', '€', '$', '¢', 'kr', 'fr', '₩', '.'
    ]

    feeds = {
        file_name: {
            'format': 'csv',
            'encoding': 'utf8',
            'store_empty': False,
            'fields': csv_columns,
            'indent': 4,
            'overwrite': True,
        }
    }

    custom_settings = {
        'FEEDS': feeds,
        'CONCURRENT_REQUESTS': 1,
        # 'DOWNLOAD_DELAY': 3,
    }

    scraped_records = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def start_requests(self):
        yield Request(url=self.base_url)

    def parse(self, response):
        for ff in self.gs_input_records[:]:
            ff['FilmFestivalName'] = str(ff['FilmFestivalName'])
            url = self.search_url_t.format(q=quote_plus(ff['FilmFestivalName']))

            meta = {
                'film_festival': ff,
                'handle_httpstatus_list': self.handle_httpstatus_list,
            }

            yield Request(url, callback=self.parse_festivals, meta=meta)

    def parse_festivals(self, response):
        for sel in response.css('.Section-browseFestivals'):
            url = sel.css('.BrowseFestivalsLink::attr(href)').get()
            name = sel.css('.BrowseFestivalsCard-name::text').get('')
            ff_name = response.meta['film_festival']['FilmFestivalName']

            if url and self.is_name_match(name, ff_name):
                return response.follow(url, callback=self.parse_details, meta=response.meta)

    def parse_details(self, response):
        organizers = self.get_organizers(response)
        deadlines = self.get_deadlines(response)
        address_values = self.get_address_values(response)
        address = get_address_parts(' '.join(address_values[:3]))

        organizers_keys = [
            'FilmFestivalDirector', 'FilmFestivalSeniorProgrammer01', 'FilmFestivalSeniorProgrammer02',
            'FilmFestivalSeniorProgrammer03', 'FilmFestivalShortsProgrammer01', 'FilmFestivalShortsProgrammer02',
        ]

        programmers = {k: name for k, name in zip(organizers_keys, organizers)}

        record = response.meta['film_festival']
        ff = {}
        ff['FilmFestivalDeadlineMonth'] = '/'.join(deadlines.pop('months'))
        # ff['FilmFestivalCountry'] = ''.join(address_values[-1:])
        ff['FilmFestivalCity'] = address['city'] or record.get('FilmFestivalCity')
        ff['FilmFestivalEmailGeneral'] = self.get_email(response)
        ff['FilmFestivalWebsite'] = self.get_website(response)
        ff['FilmFestivalAddress'] = ' '.join(address_values[:3])
        ff['FilmFestivalTelephone'] = self.get_phone(response)
        ff['FilmFestivalFacebookPage'] = self.get_facebook(response)
        ff['FilmFestivalTwitter'] = self.get_twitter_url(response)
        ff['FilmFestivalInstagramPage'] = self.get_instagram(response)
        ff['FilmFestivalRulesTerms'] = self.get_rules_terms(response)
        ff['FilmFestivalAbout'] = self.get_about_us(response)
        ff['FilmFestivalOrganizers'] = ', '.join(organizers)
        ff['FilmFestivalCategories'] = self.get_categories(response)
        ff['FilmFestivalFirstEditionYear'] = self.get_edition_year(response)
        ff['FilmFestivalFilmAge'] = self.get_years_running(response)
        # ff['FilmFestivalDeadlines'] = ', '.join(deadlines.values())
        ff['FilmFestivalDeadlineEarly'] = deadlines.get('early deadline')
        ff['FilmFestivalDeadlineRegular'] = deadlines.get('regular deadline')
        ff['FilmFestivalDeadlineLate'] = deadlines.get('late deadline')
        ff['FilmFestivalDeadlineExtended'] = deadlines.get('extended deadline')
        ff['FilmFestivalFilmfreewayLink'] = response.url

        early_fee = self.get_fee_key(response, 'Early')
        early_price = self.clean_price(early_fee)
        regular_fee = self.get_fee_key(response, 'Regular')
        regular_price = self.clean_price(regular_fee)
        late_fee = self.get_fee_key(response, 'Late')

        if not late_fee:
            late_fee = self.get_fee_key(response, 'Last')
        late_price = self.clean_price(late_fee)

        if '$' in early_fee or 'free' in early_fee.lower():
            ff['FilmFestivalFeeEarlyUSD'] = early_price
        else:
            ff['FilmFestivalFeeEarlyEUR'] = early_price

        if '$' in regular_fee or 'free' in regular_fee.lower():
            ff['FilmFestivalFeeRegularUSD'] = regular_price
        else:
            ff['FilmFestivalFeeRegularEUR'] = regular_price

        if '$' in late_fee or 'free' in late_fee.lower():
            ff['FilmFestivalFeeLateUSD'] = late_price
        else:
            ff['FilmFestivalFeeLateEUR'] = late_price

        ff.update(programmers)
        ff.update(self.get_awards(response))
        ff.update(self.get_venues(response))
        ff.update(self.get_event_types(response))

        self.scraped_records[record['FilmFestivalID']] = ff
        item = deepcopy(record)
        item.update(ff)
        yield item

    def get_name_parts(self, name):
        return [clean(e).lower() for e in name.split() if clean(e)]

    def get_deadline_month(self, date):
        return date.split('-')[1]

    def get_email(self, response):
        return response.css('a:contains("Email")::attr(href)').get('')[7:].replace('ipt:void(0)', '')

    def get_website(self, response):
        return response.css('a:contains("Website")::attr(href)').get().replace('javascript:void(0)', '')

    def get_address_values(self, response):
        # return " ".join(response.css('.break-word::text').getall()[:3])
        return response.css('[title$="on a map"]::text').getall()[:4]

    def get_phone(self, response):
        return response.css('a[href^="tel:"]::attr(href)').get('')[4:]

    def get_facebook(self, response):
        return response.css('.festival-contact-list a[href*="facebook.com"]::attr(href)').get()

    def get_twitter_url(self, response):
        return response.css('.festival-contact-list a[href*="twitter.com"]::attr(href)').get()

    def get_instagram(self, response):
        return response.css('.festival-contact-list a[href*="instagram.com"]::attr(href)').get()

    def get_rules_terms(self, response):
        return ", ".join([clean(e) for e in response.css('#rules ::text').getall() if clean(e)])

    def get_awards(self, response):
        keys = [
            'FilmFestivalAwards01', 'FilmFestivalAwards02', 'FilmFestivalAwards03',
            'FilmFestivalAwards05', 'FilmFestivalAwards06', 'FilmFestivalAwards07',
            'FilmFestivalAwards04'
        ]
        awards = ['; '.join(clean(p) for p in sel.css('p::text').getall())
                  for sel in response.css('#awards p')]

        return {k: clean(p) for k, p in zip(keys, awards) if clean(p)}

    def get_about_us(self, response):
        return ', '.join(clean(e) for e in response.css('.ProfileMiddleColumn-bioCopy ::text').getall() if clean(e))

    def get_organizers(self, response):
        designations = response.css('.festival-organizer-list dd::Text').getall()
        organizers = response.css('.festival-organizer-list dt::Text').getall()
        data = OrderedDict()
        for o, d in zip(organizers, designations):
            data[o] = d
        return data

    def get_categories(self, response):
        return ", ".join(response.css('.festival-category-name::text').getall())

    def get_deadlines(self, response):
        deadlines = {'months': []}

        for s in response.css('.ProfileFestival-datesDeadlines-headerContainer '):
            name = clean(s.css('.ProfileFestival-datesDeadlines-deadline::text').get()).lower()
            if 'deadline' in name and 'features' not in name:
                deadlines[name] = s.css('::attr(datetime)').get()
                m = s.css('.ProfileFestival-datesDeadlines-time::text').get('').split()[0]

                if m not in deadlines['months']:
                    deadlines['months'].append(m)

        return deadlines

    def get_edition_year(self, response):
        yr = clean(response.css('.ProfileFestival-sidebarHeader:contains("Years Running") + ::text').get())
        yr = yr.split()[0] if yr else 0
        return datetime.today().year - int(yr) if yr.isdigit() else ''

    def get_years_running(self, response):
        yr = clean(response.css('.ProfileFestival-sidebarHeader:contains("Years Running") + ::text').get())
        return yr.split()[0] if yr else ''

    def get_fee_key(self, response, key):
        return clean(response.css(f'.CategoryName:contains("{key}") + .Fee::text').get())

    def clean_price(self, price):
        return ''.join(e for e in (price.split(':') or ['0'])[-1] if e.strip() == '.' or e.isdigit()) or '0'

    def get_venues(self, response):
        keys = [
            'FilmFestivalVenue01', 'FilmFestivalVenue02', 'FilmFestivalVenue03',
            'FilmFestivalVenue04', 'FilmFestivalVenue05', 'FilmFestivalVenue06',
            'FilmFestivalVenue07',
        ]

        venues = {' '.join(clean(e) for e in s.css('p::text').getall() if clean(e))
                  for s in response.css('.sidebar-section:contains("Venue") li')}

        return {k: v for k, v in zip(keys, venues)}

    def get_event_types(self, response):
        event_types = [e.lower().split()[0].strip()
                       for e in response.css('.Copy::Text').getall() if e.strip()]

        et = dict(
            FilmFestivalAcademyCredited=self.is_event_exists('Academy', event_types),
            FilmFestivalBaftaCredited=self.is_event_exists('BAFTA', event_types),
            FilmFestivalCanadianSCredited=self.is_event_exists('Canadian', event_types),
            FilmFestivalGoyaCredited=self.is_event_exists('Goya', event_types),
        )

        return et

    def is_event_exists(self, event, event_types):
        return 'Yes' if event.lower() in event_types else 'No'

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FilmFreeWaySpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_idle, signals.spider_idle)
        return spider

    def spider_idle(self, spider):
        print(f"Updating values in Google Sheet...")
        self.update_gs_rows(self.scraped_records)

        print("Sleeping for 60 Minutes...")
        time.sleep(60 * 60)

        self.logger.debug("Making new request to server for Scraping Latest Prices")
        req = Request(self.base_url, dont_filter=True, priority=-100)
        self.crawler.engine.crawl(req, spider)

    def is_name_match(self, name, ff_name):
        names = self.get_name_parts(name)
        ff_names = self.get_name_parts(ff_name)
        return sum([n in ff_names for n in names]) - len(names) < 2


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(FilmFreeWaySpider)
    process.start()
