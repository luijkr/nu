"""NLP for NU.nl articles."""

import re
import json
import pymongo

from functools import partial
from collections import Counter

from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
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



def train_test(clf, params, x_train, y_train, x_test):
    """Train and test, return prediction."""
    # create grid search object
    gcv = GridSearchCV(clf, params)

    # fit model
    gcv.fit(x_train, y_train)

    # predict on test set
    y_pred = gcv.predict(x_test)

    return y_pred


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

# extract words and categories
words = []
categories = []
for article in conn.find({'article_text': {'$ne': ''}}):
    words.append(process_article(
        article['article_text'] + article['article_title']))
    categories.append(article['article_category'])

# get TF-IDF
tfidf = get_tfidf(words)

# feature hashing
hashed = feature_hashing(words, n_features=2**10)

# convert categories to numeric
le = LabelEncoder()
le.fit(list(set(categories)))
numeric_categories = le.transform(categories)

# undersample to combat class imbalance
rus = RandomUnderSampler(random_state=42)
x, y = rus.fit_sample(hashed, numeric_categories)

# split into train and test set
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=1 / 2, random_state=42)

# train random forest
params = {
    'n_estimators': range(60, 100 + 1, 10),
    'max_depth': range(2, 34 + 1, 2),
    'max_features': range(1, 10 + 1)
}

y_pred = train_test(
    clf=RandomForestClassifier(), params=params,
    x_train=x_train, y_train=y_train, x_test=x_test)

# classification report
print(classification_report(
    y_true=le.inverse_transform(y_test),
    y_pred=le.inverse_transform(y_pred)))

print(confusion_matrix(y_true=y_test, y_pred=y_pred))

# train random forest
params = {
    'n_estimators': range(60, 100 + 1, 10),
    'max_depth': range(2, 34 + 1, 2),
    'max_features': range(1, 10 + 1)
}

y_pred = train_test(
    clf=RandomForestClassifier(), params=params,
    x_train=x_train, y_train=y_train, x_test=x_test)

# classification report
print(classification_report(
    y_true=le.inverse_transform(y_test),
    y_pred=le.inverse_transform(y_pred)))

print(confusion_matrix(y_true=y_test, y_pred=y_pred))
