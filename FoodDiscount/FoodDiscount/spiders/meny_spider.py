
import scrapy
from selenium import webdriver


class MenySpider(scrapy.Spider):

    name = 'meny'
    start_urls = ['https://meny.no/Varer/Tilbud/']

    def start_request(self):

        for url in self.start_urls:
            yield scrapy.Request(url= url, callback= self.parse)

    def parse(self, response):

        # Load all products
        driver = webdriver.Firefox()
        driver.get('https://meny.no/Varer/Tilbud/')
        while True:
            try:
                button = driver.find_element_by_xpath('//*[@id="cw-loadmore-btn"]')
                button.click()
            except:
                break
        driver.close()

        all_items = response.xpath('//*[@id="cw-products-promotionpage"]/ul/li')
        for item in all_items:
            name = item.css('h3 a.cw-product__link::text').get()
            old_fee_raw = item.css('div p.cw-product__price-former::text').get()
            old_fee = old_fee_raw.replace('Før kr', '').replace(',','.').strip()
            new_fee_main = item.css('span span.cw-product__price__main::text').get()
            new_fee_decimal = item.css('span sup.cw-product__price__cents::text').get()
            new_fee = new_fee_main + '.' + new_fee_decimal
            data = {
                'name': name,
                'old fee': old_fee,
                'new fee': new_fee,
            }
            yield data
