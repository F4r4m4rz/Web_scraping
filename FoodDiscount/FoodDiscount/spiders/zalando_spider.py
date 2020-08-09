
import scrapy


class ZalandoSpider(scrapy.Spider):

    name = 'zalando'
    start_urls = ['https://www.zalando.no/salg/?sale=true']

    def start_request(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        all_items = response.xpath('//*[@id="z-nvg-cognac-root"]/div[1]/z-grid/'
                                   'z-grid-item[2]/div/div[5]/z-grid/z-grid-item')
        for item in all_items:
            name = item.css('div.cat_brandName-2XZRz.cat_ellipsis-MujnT::name').get()
            data = {
                'name': name,
            }
            yield data
