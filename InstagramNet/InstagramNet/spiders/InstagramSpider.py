import scrapy
import requests
from urllib import parse
from scrapy.utils.python import to_native_str
from InstagramNet.items import InstagramnetItem
import json

class InstagramSpider(scrapy.Spider):
    
    name = 'instaspider'
    
    custom_settings = {
        'JOBDIR' : 'crawl/instagram',
        #'LOG_FILE' : 'InstagramSpider.log',
        'LOG_LEVEL' : 'DEBUG'
    }
    
    def __init__(self):
        self.header_insta = {'x-instagram-ajax':'1',
                             'dnt':'1',
                             'referer':'https://www.instagram.com'}
        
    def start_requests(self):
        yield scrapy.Request('https://www.instagram.com',callback=self.token_login)
        
        
    # crsftoken=i23grtphjrbf3rj3yhvbrgjòfh3qrgbò; path=www.instagram.com;       
    def token_login(self,response):
        token =[to_native_str(c).split(';')[0][len('csrftoken')+1:] for c in response.headers.getlist('Set-Cookie') if to_native_str(c).startswith('csrftoken')][0] # estraggo il valore di csrftoken dai cookie
        self.header_insta['x-csrftoken'] = token
        yield scrapy.FormRequest(url='https://www.instagram.com/accounts/login/ajax/',
                    formdata={'username':'user','password': 'password'},
                    headers = self.header_insta,
                    callback=self.check_authentication) #invio i dati all'API di login
     
    def check_authentication(self,response):
        response_json = json.loads(response.text)
        start_urls = ['https://www.instagram.com/roxenne87/']
        if response_json['authenticated']:
            for url in start_urls:
                yield scrapy.Request(url,
                             headers = self.header_insta,
                             callback=self.parse_profile)
    
    def parse_profile(self,response):
        page_user = response.text
        delimitatore = 'profilePage_'
        id_utente = page_user[page_user.index(delimitatore)+len(delimitatore):page_user.index('"',page_user.index(delimitatore))]
        endpoint = 'https://www.instagram.com/graphql/query/?'
        '{"id"=4463847638,"first":20}'
        variables = '{{"id":"{}","first":{}}}'
        query = {"query_hash":"37479f2b8209594dde7facb0d904896a","variables":variables.format(id_utente,20)}
        request = scrapy.Request(endpoint+parse.urlencode(query),headers=self.header_insta,callback=self.parse_friend)
        request.meta['id_utente'] = id_utente
        request.meta['number_request'] = 1
        yield request
        
    def parse_friend(self,response):
        endpoint = 'https://www.instagram.com/graphql/query/?'
        data = json.loads(response.text)
        user = response.meta['id_utente']
        num_request = response.meta['number_request']
        for follower in data['data']['user']['edge_followed_by']['edges']:
            yield InstagramnetItem(destination=user,
                                   source=follower['node']['id'])
            yield scrapy.Request('https://www.instagram.com/'+follower['node']['username']+'/',
                             headers = self.header_insta,
                             callback=self.parse_profile)
            
        has_next = data['data']['user']['edge_followed_by']['page_info']['has_next_page']
        if has_next and num_request < 2:
            num_request = num_request + 1
            cursor = data['data']['user']['edge_followed_by']['page_info']['end_cursor']
            variables = '{{"id":"{}","first":{},"after":"{}"}}'
            query = {"query_hash":"37479f2b8209594dde7facb0d904896a","variables":variables.format(user,10,cursor)}
            request = scrapy.Request(endpoint+parse.urlencode(query),headers=self.header_insta, callback=self.parse_friend)
            request.meta['id_utente'] = user
            request.meta['number_request'] = num_request
            yield request
