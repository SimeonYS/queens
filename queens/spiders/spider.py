import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import QueensItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class QueensSpider(scrapy.Spider):
	name = 'queens'
	page = 1
	start_urls = ['https://www.qnbtrust.bank/Resources/Learning-Center/Blog/PgrID/7998/PageID/1']

	def parse(self, response):
		post_links = response.xpath('//h2/a/@href[not (ancestor::h2[@class="edn_articleTitle"])]').getall() + response.xpath('//h1/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = f'https://www.qnbtrust.bank/Resources/Learning-Center/Blog/PgrID/7998/PageID/{self.page}'
		if not len(post_links) < 10:
			self.page += 1
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		date = response.xpath('//p[@class="publish_date"]/text()').get().strip('Published on ')
		title = response.xpath('//div[@class="article standalone"]/h1/text()').get()
		content = response.xpath('//div[@class="content"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=QueensItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
