import requests
import itertools
import pymongo
from bs4 import BeautifulSoup


def get_page_links(block):
    """Finding links for content block."""
    # list all items in block, unless advertorial
    items = [
        li for li in block.findAll('li')
        if 'advertorial' not in li.attrs['data-sac-marker']
    ]

    # extract urls from item
    item_urls = ['http://www.nu.nl' + item.find('a').attrs['href'] for item in items]
    
    return item_urls


def extract_article(page_link):
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

    # article title
    article_title = soup.find('div', class_='title').find('h1').text.strip(' \n ')
    article_title = article_title.encode('ascii', 'ignore').decode('ascii')

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
        'article_text': article_text
    }

    return article



def get_articles(category):
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
    page_links = list(itertools.chain(*[get_page_links(block) for block in blocks]))
    
    print('{} articles found in "{}", scraping.'.format(str(len(page_links)), category))

    # extract article
    articles = [extract_article(page_link) for page_link in page_links]
    
    # add category
    for i in range(len(articles)):
        articles[i]['article_category'] = category

    return articles


def main():
    """Run main program."""
    # define categories to scrape
    categories = ['economie', 'sport', 'tech', 'entertainment', 'lifestyle']

    print('Start scraper for NU.nl.')

    # get current articles
    articles = [get_articles(category) for category in categories[:2]]
    articles = list(itertools.chain(*articles))

    print('Scraping done, {} articles succesfully scraped'.format(str(len(articles))))
    print('Storing in database.')

    # connect to MongoDB
    client = pymongo.MongoClient('mongodb://localhost:27017/')

    # grab database
    db = client['newsarticles']

    # add collection
    collection = db['NU']

    # add articles to database
    n_added = 0
    for article in articles:
        try:
            collection.insert_one(article)
            n_added += 1
        except:
            pass

    print('Done, {} new articles added.'.format(str(n_added)))


# run main program
main()
