import re
import scrapy
import textwrap
import unicodedata
from money_parser import price_str

class TecrootbotSpider(scrapy.Spider):
    name = "tecrootbot"
    allowed_domains = ["tecroot.lk"]
    start_urls = ["https://tecroot.lk/shop?stock=instock"]

    def parse(self, response):
        number_of_pages = response.xpath('//a[@class="page-numbers"]/text()').extract()[-1]
        print(number_of_pages)
        for page_number in range(1,int(number_of_pages)):
            page_url = f'https://tecroot.lk/shop/page/{page_number}/?stock=instock'
            yield scrapy.Request(url=page_url, callback=self.parse_page)
    
    def parse_page(self, response):
        print(response.url)
        product_url_list = response.xpath('//div[@class="product-loop-header product-item__header"]/a/@href').extract()
        for product_url in product_url_list:
            yield scrapy.Request(url=product_url, callback=self.parse_product)

    def parse_product(self, response):
        print(response.url)

        title = response.xpath('//h1[@class="product_title entry-title"]/text()').extract_first()
        availability = response.xpath('//span[@class="electro-stock-availability"]//text()').extract_first()
        description_raw = response.xpath('//div[@class="woocommerce-product-details__short-description"]//text()').extract()
        description = textwrap.shorten(re.sub( '\s+', ' ', unicodedata.normalize("NFKD",''.join(description_raw))).strip(), width=100)
        price = price_str(response.xpath('//p[@class="price"]//text()').extract()[-1])
        category = response.xpath('//nav[@class="woocommerce-breadcrumb"]//text()').extract()
        store = 'tecroot'
        image_url = response.xpath('//div[@class="product-images-wrapper"]//img/@src').extract_first()
        item_url = response.url

        print('Title    :' + '\x1b[6;30;42m' + str(title)  + '\x1b[0m')
        print('availability    :' + '\x1b[6;30;42m' + str(availability)  + '\x1b[0m')
        print('Price    :' + '\x1b[6;30;42m' + str(price)  + '\x1b[0m')
        print('store    :' + '\x1b[6;30;42m' + str(store)  + '\x1b[0m')
        print('Category :' + '\x1b[6;30;42m' + str(category)  + '\x1b[0m')
        print('Description:' + '\x1b[6;30;42m' + str(description)  + '\x1b[0m')
        print('IMG      :' + '\x1b[6;30;42m' + str(image_url)  + '\x1b[0m')
        print('URL      :' + '\x1b[6;30;42m' + str(item_url)  + '\x1b[0m')

        yield {
            'title' : title,
            'availability' : availability,
            'price' : float(price),
            'category' : category,
            'store' : store,
            'description' : description,
            'image_url' : image_url,
            'item_url' : item_url
        }