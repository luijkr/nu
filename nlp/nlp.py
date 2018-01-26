"""Text analysis."""

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


import pymongo


# connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')

# grab database
db = client['newsarticles']

# add collection
collection = db['NU']

articles = collection.find()

article = list(articles)[0]

text = article['article_text']

print(sent_tokenize(text))
print(word_tokenize(text))

stop_words = set(stopwords.words('dutch'))
word_tokens = word_tokenize(text)
filtered_sentence = [w for w in word_tokens if not w in stop_words]


for w in word_tokens:
    if w not in stop_words:
        filtered_sentence.append(w)

print(word_tokens)
print(filtered_sentence)

