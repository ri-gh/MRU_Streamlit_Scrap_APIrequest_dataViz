# -*- coding: utf-8 -*-
import pandas as pd
import datetime
from datetime import timedelta
import scrapy
from scrapy import cmdline
from scrapy.crawler import CrawlerProcess 
import os
import logging

def main():
    cmdline.execute('scrapy crawl BookingAllSpider'.split())


def hotel_data():
    list_of_cities = ['Port Louis Mauritius',
    'Vacoas Mauritius',
    'Quatre Bornes Mauritius',
    'Rose Hill Mauritius',
    'Blue Bay Mauritius',
    'Flic en Flac Mauritius',
    'Le Morne Brabant Mauritius',
    'Trou aux Biches Mauritius',
    'Grand Baie Mauritius']

    # we define the check in date as today & the check out date as today +7
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    day_plus_7 = ((datetime.datetime.now()) + timedelta(days=7))
    day_plus_7= day_plus_7.strftime("%Y-%m-%d")

    class BookingAllSpider(scrapy.Spider):
        # Name of your spider
        name = "bookingAllMRU"

        # Starting URL
        start_urls = ['https://www.booking.com/']

        # Parse function for form request
        def parse(self, response):
            for city in list_of_cities:
            
                yield scrapy.FormRequest.from_response(               
                    response,
                    formdata={ "ss": city, 
                            "data-checkin":today,
                            "data-checkout":day_plus_7,
                        
                            },
                    callback=self.after_search
                )
        # Callback used after search
        def after_search(self, response):
            
            
            results = response.css('div.a1b3f50dcd.f7c6687c3d.a1f3ecff04.f996d8c258')
                    
            for r in results:
                yield {
                    'hotel_name': r.css('h3.a4225678b2 ::text').get(),
                    'url' : r.css('h3.a4225678b2 ::attr(href)').get(),
                    'city': r.css('span.f4bd0794db.b4273d69aa ::text').get(),
                    'Score given by the website users': r.css('div.b5cd09854e.d10a6220b4::text').get(),
                    'Text description of the hotel': r.css('div.d8eab2cf7f ::text').get(),
                }

                # Name of the file where the results will be saved
    filename = "All_Booking_mru.json"

    # If file already exists, delete it before crawling (because Scrapy will concatenate the last and new results otherwise)
    if filename in os.listdir('src/'):
            os.remove('src/' + filename)

        # Declare a new CrawlerProcess with some settings
    process = CrawlerProcess (settings = {
        'USER_AGENT': 'Chrome/84.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_LEVEL': logging.INFO,
        "FEEDS": {
            'src/' + filename : {"format": "json"},
            }
    })

        # Start the crawling using the spider you defined above

    process.crawl(BookingAllSpider)
    process.start()


    datahotel =pd.read_json('src/All_Booking_mru.json')
    return datahotel

datahotel = hotel_data()
