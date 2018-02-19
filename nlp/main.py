"""NLP for NU.nl articles."""

import re
import json
import glob

from functools import partial
from collections import Counter

from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

from sklearn.feature_extraction import FeatureHasher


def clean_words(words):
    """Perform cleaning.

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


def scale_dict(d):
    """Scale a single dictionary to [0, 1]."""
    # extract values and keys
    vals = d.values()
    ks = d.keys()

    # scale to [0, 1]
    min_count = min(vals)
    max_count = max(vals) - 1
    vals = [1 + (v - min_count) / max_count for v in vals]

    return {z[0]: z[1] for z in zip(ks, vals)}


def normalized_counts(words):
    """Calculate counts, normalize them."""
    # get word counts
    counts = [Counter(w) for w in words]

    # scale to [0, 1] within document
    counts = [scale_dict(d) for d in counts]

    return counts


def feature_hashing(words, n_features):
    """Perform feature hashing."""
    # calculate normalized counts
    norm_counts = normalized_counts(words)

    # define feature hasher
    h = FeatureHasher(n_features=n_features)

    # transform into numeric array
    f = h.transform(norm_counts).toarray()[0]

    return f


def add_hash(fname):
    """Perform feature hashing and add to file."""
    # read file
    article = json.load(open(fname))

    # process article text
    words = process_article(
        article['article_text'] + article['article_title'])

    # feature hashing
    hashed = list(feature_hashing(words=[words], n_features=n_features))

    # add data to file
    article['hashed_vec'] = hashed

    # write file
    with open(fname, 'w') as file:
        json.dump(article, file)

    file.close()


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

# list of article paths
article_paths = glob.glob('articles/*.json')

# extract words, apply hash function, store in same object
n_features = 2**12
for path in article_paths:
    try:
        add_hash(path)
    except:
        pass
