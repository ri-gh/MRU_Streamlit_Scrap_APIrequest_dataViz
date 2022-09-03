# -*- coding: utf-8 -*-
import pandas as pd
import scrapy
from scrapy import cmdline
from scrapy.crawler import CrawlerProcess 
import os
import logging

a = pd.read_json('src/All_Booking_mru.json')
all_details = pd.DataFrame(a)
list_of_urls = []
for url in (all_details['url']):
    list_of_urls.append(url)


def main():
    cmdline.execute('scrapy crawl BookingAllGeoSpider'.split())


def load_data():
# we scrap lat & lon for every hotel of the df:
    class BookingAllGeoSpider(scrapy.Spider):
        # Name of your spider
        name = "allgeobookingmru"
        def start_requests(self):

            # Starting URL

            for url in list_of_urls:
                    yield scrapy.Request(url=url, callback=self.parse)
    
        def parse(self, response):
            
                results = response.css('#hotel_address') #on appelle le resultat via son id qui est unique
                for r in results:
                    yield {                               
                        'lat_lon': r.css('::attr(data-atlas-latlng)').get()}
                        

                # Name of the file where the results will be saved
    filename1 = "hotel_coord_mru.json"

            # If file already exists, delete it before crawling (because Scrapy will concatenate the last and new results otherwise)
    if filename1 in os.listdir('src/'):
                    os.remove('src/' + filename1)

    # Declare a new CrawlerProcess with some settings
    process = CrawlerProcess(settings = {
        'USER_AGENT': 'Chrome/84.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_LEVEL': logging.INFO,
        "FEEDS": {
            'src/' + filename1 : {"format": "json"},
                }
            })

            # Start the crawling using the spider you defined above
    
    process.crawl(BookingAllGeoSpider)
    process.start()
    
    datahotelgps =pd.read_json('src/hotel_coord_mru.json')
    
    return datahotelgps

datahotelgps = load_data()