# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

class DBStoringPipeline(object):
    def process_item(self, item, spider):
        try:
            with self.db:
                self.db.execute("INSERT INTO links(source, destination) VALUES(?,?)",(item['source'],item['destination']))
        except sqlite3.IntegrityError:
            print("Link gia' inserito")

    def open_spider(self,spider):
        self.db = sqlite3.connect('link_db')
        cursor = self.db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='links'")
        if not cursor.fetchone():
            self.db.execute("CREATE TABLE links(source TEXT, destination TEXT, PRIMARY KEY (source, destination))")

    def close_spider(self,spider):
        self.db.close()
