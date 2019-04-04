# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3 as lite


class InstagramnetPipeline(object):
    
    def __init__(self, sql_db, sql_table):
        self.db = sql_db
        self.table = sql_table
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            sql_db = crawler.settings.get('SQLITE3_DB'),
            sql_table = crawler.settings.get('SQLITE3_TABLE')
        )
    
    def open_spider(self,spider):
        self.connection = lite.connect(self.db)
        
    def close_spider(self,spider):
        self.connection.close()
        
    def process_item(self, item, spider):
        try:
            self.connection.execute('INSERT INTO {} VALUES ("{}","{}")'.format(self.table,item['source'],item['destination']))
            print('INSERT INTO {} VALUES ("{}","{}")'.format(self.table,item['source'],item['destination']))
            self.connection.commit()
        except lite.IntegrityError as ie:
            pass
        return item
        
