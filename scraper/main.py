"""Scraping news articles from NU.nl."""

import requests
import itertools
import time
import json
import uuid
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
        pass

    return article


# set scheduler
sched = BlockingScheduler()

# set categories to scrape
categories = ['economie', 'sport', 'tech', 'entertainment', 'lifestyle']


@sched.scheduled_job('interval', minutes=30)
def main(categories=categories):
    """Run main program every hour."""
    print('Starting main program.')

    # set log file
    fname = 'logs/{}.log'.format(
        time.strftime(
            "%Y_%m_%d-%H_%M_%S", time.localtime()
        )
    )
    logfile = open(fname, 'w')

    logfile.write('Start scraper for NU.nl.\n')

    # get urls of already scraped pages
    done_fname = 'urls_done.csv'
    done_file = open(done_fname, 'w+')
    done_urls = [line.strip(';') for line in done_file]

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
        logfile.write('Category "{}", scraping {} new pages\n'.format(
            category, len(urls))
        )
        for url in urls:
            print(url)
            done_file.write(url + ';')

            # scrape article
            article = scrape_article(url)

            # add article category
            article['article_category'] = category

            # save to file
            out_fname = 'articles/{}.json'.format(str(uuid.uuid4()))
            with open(out_fname, 'w') as outfile:
                json.dump(article, outfile)

            outfile.close()

    # close logging file
    logfile.close()


# start scheduler, running every 30 mins
sched.start()
