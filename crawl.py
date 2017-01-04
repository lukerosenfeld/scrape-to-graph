import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

import networkx as nx
import pickle


badstatuses = open("badstatuses.txt", "w")
graphnodes = open("graphnodes.json", "w")
centrality_info = open("centrality_info.json", "w")


class CrawlSpider(scrapy.Spider):
    abbreviated_domain = input('Enter the domain you would like to crawl: ')
    full_domain = "https://www" + abbreviated_domain
    len_domain = len(full_domain)

    rules = (Rule(LinkExtractor(), callback='parse', follow=True), )

    def __init__(self):
        self.id_count = 0
        self.url_id_mapping = dict()
        self.G = nx.DiGraph()
        self.failed_urls = []
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        print("dumping graph object to binary file...")
        pickle.dump(self.G, open('scraped-graph.txt', 'wb'))
        
        print("writing found 404s to file...")
        badstatuses.write(str(self.failed_urls))

        print("creating json object of nodes and id mapping...")
        graphnodes.write(str(self.url_id_mapping).replace('\'','\"'))
        graphnodes.write("\n")
        inv_url_id_map = {v: k for k, v in self.url_id_mapping.items()}
        graphnodes.write(str(inv_url_id_map).replace('\'','\"'))

        execfile("comparesitemap.py")

    def parse(self, response):
        thispage = response.url
        if response.status != 200:
            self.failed_urls.append({"error on":response.url,"status":response.status, "referer":response.request.headers.get('Referer', None)})

        robots = ["fake", "robots", "items"]

        if not any(x in str(thispage) for x in robots):
            thispage = str(thispage)[len_domain:]
            for href in response.css("a::attr('href')"):
                url = response.urljoin(href.extract())
                urlstring = str(url)
                if not any(x in urlstring for x in robots):
                    newnodestring = newnode[len_domain:]
                    self.add_new_edge(thispage, newnodestring)
                    
                    if abbreviated_domain in newnode:
                        yield scrapy.Request(newnode, callback=self.parse)

    def add_new_node(self, nodename):
        if nodename not in self.url_id_mapping:
            if nodename not in self.G.nodes():
                self.id_count += 1
                self.url_id_mapping[nodename] = self.id_count
                self.G.add_node((nodename,self.id_count))
        
    def add_new_edge(self, origin, dest):
        if origin not in self.G.nodes():
            if origin not in self.url_id_mapping:
                self.id_count+=1
                self.url_id_mapping[origin] = self.id_count
            if dest not in self.url_id_mapping:
                self.id_count+=1
                self.url_id_mapping[dest] = self.id_count
            self.G.add_edge(self.url_id_mapping[origin], self.url_id_mapping[dest])
