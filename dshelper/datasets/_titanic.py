"""Titanic dataset.

A classic titanic dataset for survival prediction.
The dataset page is available from Kaggle
https://www.kaggle.com/c/titanic
"""

import os
from pathlib import Path
import datetime

import pandas as pd
import numpy as np


def fetch_titanic(with_random_date=False):
    dir_path = Path(__file__).parent.parent.absolute()
    csv_filename = os.path.join(dir_path, "datasets", "data", "titanic.csv")
    df = pd.read_csv(csv_filename)

    if with_random_date:
        # Insert some random dates into the df
        random_dates = [
            datetime.date(2016, 1, 1) + datetime.timedelta(days=int(days))
            for days in np.random.randint(1, 50, df.shape[0])
        ]
        # Insert to df
        df.insert(0, "Random Date", random_dates)

    return df
