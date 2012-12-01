#coding: utf-8

import requests
from BeautifulSoup import BeautifulSoup
from xml.dom.minidom import Document
from datetime import datetime
import rfc822
import sys
import os
import redis

def update_index():
    url_index = 'http://www.cowonglobal.com/zeroboard/zboard.php?id=C08&bmenu=support'
    r = requests.get(url_index)
    soup = BeautifulSoup(r.text)
    select = soup.find('select')
    options = select.findAll('option')
    index = {}
    for option in options:
        if option['value'] != '':
            index.update({option['value']: option.text})
    return index



class CowonRss():

    def __init__(self, category_id, category_name):
        self.data_dict =  {'page': '1',
                      'id': 'C08',
                      'select_arrange': 'headnum',
                      'desc': 'asc',
                      'page_num': '20',
                      'selected': '',
                      'exec': '',
                      'sn':'off',
                      'ss':'on',
                      'sc':'on',
                      'category':'',
                      'bmenu':'support',
                      'keyword': ''}

        self.url = "http://www.cowonglobal.com/zeroboard/zboard.php"
        self.category_id = category_id
        self.category_name = category_name
        self.data_dict.update({'category': category_id})

    def parse_items(self):
        req = requests.post(self.url, data=self.data_dict)
        soup = BeautifulSoup(req.text)
        self.items = []
        for link in soup.findAll('a', **{'class': 'list_link'}):
            param = {}
            param['link'] = 'http://www.cowonglobal.com/zeroboard/%s' % link['href']
            req_item = requests.get(param['link'])
            soup_item = BeautifulSoup(req_item.text)
            param['title'] = soup_item.find('td', **{'class': 'board_title'}).text
            src_date = soup_item.findAll('td', **{'class': 't9_4a4d4a'})[1].text
            date = datetime.strptime(src_date, '%d-%m-%Y %H:%M:%S')
            param['date'] = rfc822.formatdate(rfc822.mktime_tz(rfc822.parsedate_tz(date.strftime("%a, %d %b %Y %H:%M:%S"))))
            body_text = soup_item.find('table', **{'class': 'body'})
            if body_text:
                param['text'] = body_text.text
            else:
                param['text'] = 'None'
            self.items.append(param)


    def rss(self):
        doc = Document()
        rss = doc.createElement("rss")
        rss.setAttribute("version", "2.0")
        channel = doc.createElement("channel")
        title = doc.createElement("title")
        link = doc.createElement("link")

        description = doc.createElement("description")

        title_text = doc.createTextNode(self.category_name + " firmware updates")
        link_text = doc.createTextNode("http://www.cowonglobal.com/zeroboard/zboard.php?id=C08&bmenu=support")
        description_text = doc.createTextNode(self.category_name + " firmware updates")

        link.appendChild(link_text)
        title.appendChild(title_text)
        description.appendChild(description_text)

        channel.appendChild(title)
        channel.appendChild(link)
        channel.appendChild(description)

        for item in self.items:
            rss_item = doc.createElement("item")
            rss_link = doc.createElement("link")
            rss_title = doc.createElement("title")
            rss_description = doc.createElement("description")
            rss_pub_date = doc.createElement("pubDate")


            rss_link_text = doc.createTextNode(item['link'])
            rss_title_text = doc.createTextNode(item['title'])
            rss_date_text = doc.createTextNode(item['date'])
            rss_description_text = doc.createTextNode(item['text'])

            rss_link.appendChild(rss_link_text)
            rss_title.appendChild(rss_title_text)
            rss_description.appendChild(rss_description_text)
            rss_pub_date.appendChild(rss_date_text)

            rss_item.appendChild(rss_link)
            rss_item.appendChild(rss_title)
            rss_item.appendChild(rss_description)
            rss_item.appendChild(rss_pub_date)

            channel.appendChild(rss_item)
        rss.appendChild(channel)
        doc.appendChild(rss)
        return doc.toprettyxml(indent="  ")



if __name__ == "__main__":
    r = redis.from_url(os.environ['REDISTOGO_URL'])
    main_index = update_index()
    if len(main_index) == 0:
        sys.exit()
    index_html = ""
    for category_id, category_name in main_index.items():
        index_html += "<li><a href='/static/%s.rss'>%s</a></li>" % (category_id, category_name)
    index_html = "<html><head></head><body><ul>%s</ul><br>last update: %s</body>" % (index_html, datetime.now().isoformat())
    r.set('index.html', index_html)

    for category_id, category_name in main_index.items():
        cowon_rss = CowonRss(category_id, category_name)
        cowon_rss.parse_items()
        try:
            r.set('%s.rss' % category_id, cowon_rss.rss())
        except UnicodeEncodeError:
            r.set('%s.rss' % category_id, 'error')
