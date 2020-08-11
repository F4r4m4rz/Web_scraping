from time import sleep

import scrapy
from selenium import webdriver


class MenySpider(scrapy.Spider):

    name = 'meny'
    start_urls = ['https://meny.no/Varer/Tilbud/']
    driver = None
    DATA = []

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.get(self.start_urls[0])
        while True:
            try:
                button = self.driver.find_element_by_xpath('//*[@id="cw-loadmore-btn"]')
                button.click()
            except:
                break

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
                old_fee_main = product_details.find_element_by_css_selector('span > span.cw-product__price__main').text
                try:
                    old_fee_cent = product_details.find_element_by_css_selector('span>sup.cw-product__price__cents').text
                except:
                    old_fee_cent = '00'
                old_fee = old_fee_main + '.' + old_fee_cent

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
            self.DATA.append(data)
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
        with open("template.txt") as file:
            html = self.make_html(file.read())

        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        with smtplib.SMTP(host='smtp-mail.outlook.com', port=587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )

    def make_html(self, template : str):
        body = """<table style= "width: 100%; border: 1px solid black;">
            <tr>
                <th style="border: 1px solid black;">No</th> 
                <th style="border: 1px solid black;">Name</th>
                <th style="border: 1px solid black;">Old fee</th>
                <th style="border: 1px solid black;">New fee</th>
                <th style="border: 1px solid black;">Deal</th>
                <th style="border: 1px solid black;">link</th>
            </tr>
            #ROWS#
        </table>"""
        rows = ""
        no = 1
        for a in self.DATA:
            row=f"""
            <tr>
                <td style="border: 1px solid black;">{no}</td>
                <td style="border: 1px solid black;">{a["name"]}</td>
                <td style="border: 1px solid black;">{a["old fee"]}</td>
                <td style="border: 1px solid black;">{a["new fee"]}</td>
                <td style="border: 1px solid black;">{a["deal"]}</td>
                <td style="border: 1px solid black;"><a>{a["link"]}</a></td>
            </tr>
            """
            rows = rows + row
            no += 1

        body = body.replace("#ROWS#", rows)
        return template.replace("#Body#", body)

