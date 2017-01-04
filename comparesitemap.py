import requests
import re
import json

sitemapurls = open("sitemapurls.txt", "w")
SITEMAP_URL = input('Enter your sitemap url: ')
sitemap = requests.get(SITEMAP_URL)
subsitemaps = re.findall(r'<loc>(.*?)</loc>', sitemap.text)
for sub in subsitemaps:
	getsubsitemap = requests.get(sub)
	suburls = re.findall(r'<loc>(.*?)</loc>', getsubsitemap.text)
	for url in suburls:
		sitemapurls.write(url[23:] + ",")

sitemapurls.close()

print("finished collecting sitemap urls!")
print("comparing sitemap urls to nodes in crawled graph...")

graphdata = open('graphnodes.json', 'r')
url_mapping = json.loads(graphdata.readline())
graphnodesdict = dict(url_mapping)
graphdata.close()

missingurlsfromgraph = open("missing_urls.txt", "w")

readsitemapurls = open('sitemapurls.txt', 'rb')
readsitemapurls = readsitemapurls.read().split(',')
sitemapurlsset = set()
for x in readsitemapurls:
	sitemapurlsset.add(x)

graphurlset = set()
for y in graphnodesdict.keys():
	graphurlset.add(y)

missingurlsfromgraph.write(str(sitemapurlsset.difference(graphurlset))) # the urls that are in the sitemap but not the graph

print("done - see missing_urls.txt for the list of urls in the sitemap that were not found by scraping")

