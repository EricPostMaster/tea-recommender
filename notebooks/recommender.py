import pickle
import pandas as pd
from surprise import BaselineOnly, Dataset
from surprise import Reader
from surprise import SVD, KNNBasic
from surprise import NormalPredictor
from surprise.model_selection import cross_validate

with open("../data/pickled-data/tea_dict.p", 'rb') as p:
    tea_dict = pickle.load(p)

# print(tea_dict['Forever Nuts'])

ratings = []

for tea in tea_dict.keys():
    for tea_char in tea_dict[tea].keys():
        if tea_char == 'reviewers':
            for reviewer in tea_dict[tea][tea_char].keys():
                ratings.append((reviewer, tea, tea_dict[tea][tea_char][reviewer]['weight']))

df = pd.DataFrame(ratings, columns=['user', 'item', 'rating'])

reader = Reader(rating_scale=(0,100))

data = Dataset.load_from_df(df[['user', 'item', 'rating']], reader)

murph = cross_validate(NormalPredictor(), data, cv=2)

cross_validate(BaselineOnly(), data, cv=2, verbose=True)

cross_validate(SVD(), data, cv=2)

cross_validate(KNNBasic(), data, cv=2)


