"""NLP for NU.nl articles."""

import re
import json
import pymongo

from functools import partial

from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords


def clean_words(words):
    """
    Perform cleaning.

    Convert to lower case, remove non-letter characters, remove stop words,
    remove very short words.
    """
    rxp = r'[^a-z]'
    words = [re.sub(rxp, '', w.lower()) for w in words]
    words = [
        w for w in words
        if w != '' and w not in stop_words and len(w) > 2
    ]

    return words


def get_bag_of_words(text):
    """Extract unique words, returns cleaned words."""
    # tokenize text, returning list of words
    words = tokenizer(text)

    # clean words, removing interpunction
    words = clean_words(words)

    return words


def get_bag_of_stems(text):
    """Extract bag of words, and stems each word."""
    # get bag of words
    words = get_bag_of_words(text)

    # take stems of each word
    stems = [stemmer(w) for w in words]

    return stems


def process_article(article_text):
    """Process article text."""
    # get list of cleaned words
    words = get_bag_of_words(article_text)

    # get list of cleaned stems
    stems = get_bag_of_stems(article_text)

    # combine
    inputs = list(set.union(set(words), set(stems)))

    return inputs


# define NL tokenizer
tokenizer = partial(word_tokenize, language='dutch')

# define NL stemmer
stemmer = SnowballStemmer('dutch').stem

# get NL stop words
include_custom = False
stop_words_nltk = set(stopwords.words('dutch'))
stop_words_custom = set(json.load(open('nlp/custom_stopwords.json'))['nl'])
if include_custom:
    stop_words = set.union(stop_words_nltk, stop_words_custom)
else:
    stop_words = set(stop_words_nltk)


# connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')

# grab data from database, collection NU
db = client['newsarticles']
collection = db['NU']
articles = collection.find()

# list of cleaned words per article
words = [
    process_article(article['article_text'] + article['article_title'])
    for article in articles
]
