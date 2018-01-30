"""NLP for NU.nl articles."""

import re
import json
import pymongo

import numpy as np

from functools import partial

from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction import FeatureHasher


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
    """Process article text by stemming and cleaning."""
    stems = get_bag_of_stems(article_text)

    return stems


def get_tfidf(words):
    """Calculate TF-IDF matrix."""
    # get word counts
    count_vect = CountVectorizer(strip_accents='unicode')
    counts = count_vect.fit_transform([' '.join(w) for w in words])

    # Term-Frequency Inverse-Document Frequency transformation
    tfidf = TfidfTransformer(sublinear_tf=True).fit_transform(counts)
    
    return tfidf


def normalized_counts(words):
    """Calculate counts, normalize them."""
    # get word counts
    count_vect = CountVectorizer(strip_accents='unicode')
    counts = count_vect.fit_transform([' '.join(w) for w in words])
    
    # scale to [0, 1] within document
    
    
    # 


def feature_hashing(words, n_features):
    """."""
    # define feature hasher
    h = FeatureHasher(n_features=n_features)

    # transform into numeric array
    f = h.transform(tf).toarray()

    return f


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

# grab collection from within database
conn = client['newsarticles']['NU']

# extract articles
articles = list(conn.find({'article_text': {'$ne': ''}}))

# article category
categories = [article['article_category'] for article in articles]

# list of cleaned words per article
words = [
    process_article(article['article_text'] + article['article_title'])
    for article in articles
]

# get counts
counts = [Counter(w) for w in words]

# get TF-IDF
tfidf = get_tfidf(words)


from collections import Counter

h.transform(Counter(words[0]))