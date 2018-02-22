"""Prediction for NU.nl articles."""

# data handlers
import json
import glob
import numpy as np

# sparse matrices
from scipy.sparse import csr_matrix, vstack

# preprocessing
from sklearn.preprocessing import LabelEncoder, scale

# modelling
from sklearn.linear_model import LogisticRegression

# model selection
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import StratifiedKFold

# model evaluation
from sklearn.metrics import classification_report, confusion_matrix


def read_data():
    """Read hashed vectors."""
    # list paths to articles
    article_paths = glob.glob('articles/*.json')

    # read data in matrix, store categories
    data = []
    categories = []
    check_keys = [
        'article_category', 'hashed_vec', 'n_words', 'n_unique',
        'prop_unique', 'n_chars', 'n_chars_word',
        'n_quotes', 'n_quotes_word',
    ]
    for path in article_paths:
        try:
            # read article data
            article = json.load(open(path))

            # check if all necessary keys are stored in this file
            indx = [key in article.keys() for key in check_keys]
            if np.all(indx):
                categories.append(article['article_category'])

                # hashed text
                hash_mat = article['hashed_vec']

                # other engineerd features
                eng_feats = [
                    np.log10(article['n_words']),
                    np.log10(article['n_unique']),
                    float(article['n_unique'] > 6.38),
                    article['prop_unique'],
                    np.log10(article['n_chars']),
                    article['n_chars_word'],
                    article['n_quotes'],
                    article['n_quotes_word'],
                    float(article['n_quotes'] > 0),
                ]

                # add to data
                data.append(csr_matrix(hash_mat + eng_feats))
            else:
                pass
        except:
            pass

    data = vstack(data)

    return data, categories


def evaluate(y_pred, y_true):
    """Evaluate prediction accuracy."""
    # classification report
    print(classification_report(
        y_true=y_true,
        y_pred=y_pred
    ))

    # confusion matrix
    print(confusion_matrix(y_true=y_true, y_pred=y_pred))


def train_test(clf, params, cv, x_train, y_train, x_test, y_test):
    """Train and test, return prediction."""
    # create grid search object
    gcv = GridSearchCV(clf, params, cv=cv)

    # fit model
    gcv.fit(x_train, y_train)
    print(gcv.best_params_)

    # predict on test set
    y_pred = gcv.predict(x_test)

    evaluate(
        y_pred=le.inverse_transform(y_pred),
        y_true=le.inverse_transform(y_test)
    )


# read data
data, categories = read_data()

# convert categories to numeric
le = LabelEncoder()
le.fit(list(set(categories)))
numeric_categories = le.transform(categories)

# split into train and test set
x_train, x_test, y_train, y_test = train_test_split(
    data, numeric_categories, test_size=0.5)

# scale data
scale(x_train.toarray(), axis=0)
scale(x_test.toarray(), axis=0)

# stratified k-fold
cv = StratifiedKFold(n_splits=5, shuffle=True)

# one-vs-rest logistic regression
train_test(
    clf=LogisticRegression(multi_class='ovr'), cv=cv,
    params={
        'C': np.linspace(0.001, 5, num=20),
        'penalty': ['l1'],
    },
    x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)
