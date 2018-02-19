"""NLP for NU.nl articles."""

import json
import glob
import numpy as np

from scipy.sparse import csr_matrix, vstack
from imblearn.under_sampling import RandomUnderSampler

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.linear_model import LogisticRegression


def read_data():
    """Read hashed vectors."""
    # list paths to articles
    article_paths = glob.glob('articles/*.json')

    # read data in matrix, store categories
    data = []
    categories = []
    for path in article_paths:
        try:
            article = json.load(open(path))
            new_mat = csr_matrix(article['hashed_vec'])
            new_cat = article['article_category']
            data.append(new_mat)
            categories.append(new_cat)
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


def train_test(clf, params, x_train, y_train, x_test, y_test):
    """Train and test, return prediction."""
    # create grid search object
    gcv = GridSearchCV(clf, params)

    # fit model
    gcv.fit(x_train, y_train)
    print(gcv.best_params_)

    # predict on test set
    y_pred = gcv.predict(x_test)

    evaluate(y_pred=y_pred, y_true=y_test)


# read data
data, categories = read_data()

# check number of articles in each category
print(np.unique(categories, return_counts=True))

# filter on selected categories
selected = ['economie', 'sport', 'tech', 'entertainment']
indx = np.array([val in selected for val in categories])
data = data[indx, ]
categories = np.array(categories)[indx]

# convert categories to numeric
le = LabelEncoder()
le.fit(list(set(categories)))
numeric_categories = le.transform(categories)

# undersample to combat class imbalance
rus = RandomUnderSampler(random_state=42)
x, y = rus.fit_sample(data, numeric_categories)

# split into train and test set
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.5, random_state=42)

# one-vs-all logistic regression; accuracy = 0.97
train_test(
    clf=LogisticRegression(multi_class='ovr'),
    params={
        'C': np.linspace(0.01, 0.5, num=100),
        'penalty': ['l2'],
    },
    x_train=x_train, y_train=y_train, x_test=x_test, y_test=y_test)
