from time import sleep

import scrapy
from selenium import webdriver


class MenySpider(scrapy.Spider):

    name = 'meny'
    start_urls = ['https://meny.no/Varer/Tilbud/']
    driver = None

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get(self.start_urls[0])
        #while True:
        #    try:
        #        button = self.driver.find_element_by_xpath('//*[@id="cw-loadmore-btn"]')
        #        button.click()
        #    except:
        #        break

    def parse(self, response):
        all_items = self.driver.find_elements_by_xpath('//*[@id="cw-products-promotionpage"]/ul/li')
        for item in all_items:
            try:
                unavailable = item.find_element_by_class_name('cw-product__unavailable')
                continue
            except:
                pass

            product_details = item.find_element_by_class_name('cw-product__details')

            # new fee
            new_fee_main = product_details.find_element_by_css_selector('span > span.cw-product__price__main').text
            try:
                new_fee_cent = product_details.find_element_by_css_selector('span>sup.cw-product__price__cents').text
            except:
                new_fee_cent = '00'

            new_fee = new_fee_main + '.' + new_fee_cent

            # old fee
            try:
                old_fee_raw = product_details.find_element_by_css_selector('p.cw-product__price-former')
                old_fee = old_fee_raw.text.replace('FØR KR', '').replace(',', '.').strip()
            except:
                new_fee = '-'
                old_fee_main = product_details.find_element_by_css_selector('span > span.cw-product__price__main')
                old_fee_cent = product_details.find_element_by_css_selector('span>sup.cw-product__price__cents')
                old_fee = old_fee_main.text + '.' + old_fee_cent.text

            # deal
            try:
                deal = product_details\
                    .find_element_by_css_selector('div.cw-product__additioal-info>a.cw-product__promotion').text
            except:
                deal = '-'

            # Title
            h3 = item.find_element_by_class_name('cw-product__title')
            name = h3.find_element_by_class_name('cw-product__link')
            link = name.get_attribute('href')
            data = {
                'name': name.text,
                'old fee': old_fee,
                'new fee': new_fee,
                'deal': deal,
                'link': link,
            }
            yield data
        self.send_email()

    def __del__(self):
        self.driver.close()
        #self.send_email()

    def send_email(self):
        import smtplib, ssl
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        sender_email = "faramarz.bodaghi@outlook.com"
        receiver_email = "akram.yousefi@gmail.com"
        with open('pass.txt') as file:
            password = file.readline().strip()

        message = MIMEMultipart("alternative")
        message["Subject"] = "test"
        message["From"] = sender_email
        message["To"] = receiver_email

        text = """\
        Hi,
        How are you?"""

        part1 = MIMEText(text, "plain")
        message.attach(part1)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        with smtplib.SMTP_SSL(host='smtp-mail.outlook.com', port=587) as server:

            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
