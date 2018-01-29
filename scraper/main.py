"""Scraping news articles from NU.nl."""

import requests
import itertools
import pymongo
import time
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler


def get_page_links(category):
    """Get links to listed articles."""
    # create overview link
    url_overview = 'http://www.nu.nl/{}'.format(category)

    # make request using splash
    r = requests.post(
        'http://localhost:8050/render.html',
        json={
            'url': url_overview,
            'http_method': 'POST',
            'body': 'a=b',
            'wait': 0.5
        }
    )

    # parse html
    soup = BeautifulSoup(r.content, 'html.parser')

    # find page links
    blocks = soup.findAll('div', class_='block articlelist')
    page_links = list(itertools.chain(*[
        get_block_links(block) for block in blocks
    ]))

    return page_links


def get_block_links(block):
    """Finding links for content block."""
    # list all items in block, unless advertorial
    items = [
        li for li in block.findAll('li')
        if 'advertorial' not in li.attrs['data-sac-marker']
    ]

    # extract urls from item
    item_urls = [
        'http://www.nu.nl' + item.find('a').attrs['href']
        for item in items if 'hasvideo' not in item.attrs['class']
    ]

    return item_urls


def scrape_article(page_link):
    """Scrape article text."""
    # make request using splash
    r = requests.post(
        'http://localhost:8050/render.html',
        json={
            'url': page_link,
            'http_method': 'POST',
            'body': 'a=b',
            'wait': 0.5
        }
    )

    # parse html
    soup = BeautifulSoup(r.content, 'html.parser')

    # try scraping the article
    try:
        # article title
        article_title = soup.find('div', class_='title')
        article_title = article_title.find('h1').text.strip(' \n ')

        # find block with article text
        article_body = soup.find('div', class_='block article body')

        # extract all paragraph text
        article_text = ' '.join([
            p.text.encode('ascii', 'ignore').decode('ascii')
            for p in article_body.findAll('p')
        ])

        # put in dict
        article = {
            'article_title': article_title,
            'article_text': article_text,
            'article_url': page_link,
            'scrape_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }
    except:
        # create dict without text
        article = {
            'article_title': '',
            'article_text': '',
            'article_url': page_link,
            'scrape_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

    return article


# set scheduler
sched = BlockingScheduler()

# set categories to scrape
categories = ['economie', 'sport', 'tech', 'entertainment', 'lifestyle']


@sched.scheduled_job('interval', minutes=30)
def main(categories=categories):
    """Run main program every hour."""
    # set log file
    fname = 'logs/{}.log'.format(
        time.strftime(
            "%Y_%m_%d-%H_%M_%S", time.localtime()
        )
    )
    file = open(fname, 'w')

    file.write('Start scraper for NU.nl.\n')

    # connect to MongoDB
    client = pymongo.MongoClient('mongodb://localhost:27017/')

    # grab collection from within database
    conn = client['newsarticles']['NU']

    # get urls of already scraped pages
    done_urls = conn.find({}, {'article_url': 1})
    done_urls = [du['article_url'] for du in done_urls]

    # get page links per category
    page_links = {
        category: [
            pl for pl in get_page_links(category)
            if pl not in done_urls
        ]
        for category in categories
    }

    # scrape articles
    for category in categories:
        urls = page_links[category]
        file.write('Category "{}", scraping {} new pages\n'.format(
            category, len(urls))
        )
        for url in urls:
            # scrape article
            article = scrape_article(url)

            # add article category
            article['article_category'] = category

            # store in database
            conn.insert_one(article)

    # close logging file
    file.close()


# start scheduler, running every hour
sched.start()
