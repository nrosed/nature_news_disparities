
from collections import defaultdict
from random import sample, seed
import scrapy
import re
from datetime import datetime
from nature_news_scraper.spiders import article_crawl

class NewsSpider(scrapy.Spider):
    name = "author_crawl"

    def start_requests(self):

        year = int(self.target_year)
        type_article = self.target_type

        url = 'https://www.nature.com/nature/articles?type=%s&year=%d' % (type_article, year)


        yield scrapy.Request(url=url, callback=self.parse_article_list, cb_kwargs=dict(year=year), dont_filter=True)

    def parse_article_list(self, response, year=None):
        # produce a bunch of scrape tasks for each article on the page
        # and finally produce a task for the next page, if it exists

        # here (and all other places) we are using attribute selectors in CSS 
        articles = response.css('article[itemtype="http://schema.org/ScholarlyArticle"]')

        for article in articles:
            link = article.css('a[itemprop="url"]::attr(href)').get()

            if link is not None:
                full_link = response.urljoin(link)
                print("Article: %s" % full_link)
                yield scrapy.Request(url=full_link, callback=self.parse_article, cb_kwargs=dict(year=year), dont_filter=True)


        # also see if there's a next page and yield that, too
        next_page = response.css('ul.c-pagination > li[data-page="next"] > a::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            print("next page: %s" % next_page)
            yield scrapy.Request(next_page, callback=self.parse_article_list, cb_kwargs=dict(year=year))


    def parse_article(self, response, year=None):

        import re

        # # get author names

        # get meta tags, process in order since there can be any number of citation_author_institutions following a citation_author
        author_metas = response.css('meta[name^="citation_author"]')
        authors = []
        curAuthor = None
        for meta in author_metas:
            meta_name = meta.css('::attr(name)').get()
            meta_content = meta.css('::attr(content)').get().strip()
            if meta_name == 'citation_author':
                if curAuthor:
                    authors.append(curAuthor)
                curAuthor = {'name': meta_content, 'affiliation': ''}
            elif meta_name == 'citation_author_institution' and curAuthor is not None:
                curAuthor['affiliation'] += ' ' + meta_content
            else:
                raise Exception("unrecognized meta tag %s with content %s" % (meta_name, meta_content))

        authors_mapped = [
            {'name': x['name'].strip(), 'affiliation': ", ".join(x['affiliation'].strip().split(",")[:]).strip()}
            for x in authors
        ]

        yield {
           "file_id": response.url.split("/")[-1],
           "year": year,
           "authors": authors_mapped
        }

