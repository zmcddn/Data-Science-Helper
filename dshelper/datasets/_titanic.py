"""Titanic dataset.

A classic titanic dataset for survival prediction.
The dataset page is available from Kaggle
https://www.kaggle.com/c/titanic
"""

import os
import datetime

import pandas as pd
import numpy as np


def fetch_titanic(with_random_date=False):
    try:
        # Import as module, use absolute path
        dir_path = os.path.abspath(os.path.dirname("train.csv"))
        csv_filename = os.path.join(dir_path, "dshelper\\datasets\\data\\titanic.csv")
        df = pd.read_csv(csv_filename)
    except FileNotFoundError:
        # Run as function, use relative path
        df = pd.read_csv("./datasets/data/titanic.csv")

    if with_random_date:
        # Insert some random dates into the df
        random_dates = [
            datetime.date(2016, 1, 1) + datetime.timedelta(days=int(days))
            for days in np.random.randint(1, 50, df.shape[0])
        ]
        # Insert to df
        df.insert(0, "Random Date", random_dates)

    return df
