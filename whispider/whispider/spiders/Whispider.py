import scrapy
from bs4 import BeautifulSoup as bs
from whispider.items import LinkItem
from urllib import parse

class WhiSpider(scrapy.Spider):

    name = 'whispider'

    def start_requests(self): #genero la richiesta iniziale alla pagina di login
        yield scrapy.Request('https://weheartit.com/login')

    def parse(self, response):
        xhtml_tree = bs(response.text,'lxml')
        authenticity_token = xhtml_tree.find('input',{'name':'authenticity_token'}).attrs['value']
        dati_form = {'authenticity_token': authenticity_token,
                    'user[password]':'SomeniLab',
                    'user[email]':'somenilab@gmail.com'}
        return scrapy.FormRequest(url='https://weheartit.com/login/authenticate', formdata = dati_form, callback = self.after_login)

    def after_login(self, response):
        return scrapy.Request('https://weheartit.com/settings', callback = self.check_login)

    def check_login(self, response):
        if response.text.find('somenilab') != -1:
            yield scrapy.Request('https://weheartit.com/pekmarifetli/contacts', callback = self.parse_friends)
            yield scrapy.Request('https://weheartit.com/pekmarifetli/fans', callback = self.parse_fans)

    def parse_friends(self, response):
        source = response.url.split('/')[3]
        xpath_selection_maxpage = "//div[@id='content']/@data-infinite-scroll-count"
        if not parse.parse_qs(parse.urlsplit(response.url).query):
            if response.selector.xpath(xpath_selection_maxpage).get():
                for i in range(2,min(10, int(response.selector.xpath(xpath_selection_maxpage).get()))):
                    yield scrapy.Request('https://weheartit.com/{}/contacts?scrolling=true&page={}'.format(source,i), callback=self.parse_friends)
        xpath_selection_friends = "//div[contains(@class,'js-user-info')]//a[contains(@class,'avatar-container')]/@href"
        for e in response.selector.xpath(xpath_selection_friends).getall():
            #yield {'source': source , 'destination': e[1:]}
            yield LinkItem(source = source, destination = e[1:])
            yield scrapy.Request('https://weheartit.com{}/contacts'.format(e), callback=self.parse_friends)

    def parse_fans(self, response):
        source = response.url.split('/')[3]
        xpath_selection_maxpage = "//div[@id='content']/@data-infinite-scroll-count"
        if not parse.parse_qs(parse.urlsplit(response.url).query):
            if response.selector.xpath(xpath_selection_maxpage).get():
                for i in range(2,min(10, int(response.selector.xpath(xpath_selection_maxpage).get()))):
                    yield scrapy.Request('https://weheartit.com/{}/fans?scrolling=true&page={}'.format(source,i), callback=self.parse_fans)
        xpath_selection_friends = "//div[contains(@class,'js-user-info')]//a[contains(@class,'avatar-container')]/@href"
        for e in response.selector.xpath(xpath_selection_friends).getall():
            #yield {'source': e[1:] , 'destination': source}
            yield LinkItem(source = e[1:], destination = source)
            yield scrapy.Request('https://weheartit.com{}/fans'.format(e), callback=self.parse_friends)
