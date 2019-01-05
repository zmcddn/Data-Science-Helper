import pandas as pd
import numpy as np
from numpy import arange, sin, pi

from wx.lib.pubsub import pub

from sklearn.preprocessing import LabelEncoder


def prepare_data(df):
    """
    A helper function to prepare the data for plot.

    The way it cleans follows the standard data science way of cleaning:
        categorical data: 
            encode with LabelEncoder
            fillna with mode
        numerical data:
            fillna with median

    input: raw data frame
    output: data frame with encoded categorical data and without any null data
    """

    label = LabelEncoder()

    start_message = "\nPrepare data for plotting ..."
    pub.sendMessage("LOG_MESSAGE", log_message=start_message)
    _spacing = " " * 7

    encoding_drop_columns = []
    for num, column_type in enumerate(df.dtypes):
        original_column_name = df.columns[num]
        _message = "--> Processing column: {} --> {}".format(
            original_column_name, column_type
        )
        pub.sendMessage("LOG_MESSAGE", log_message=_message)

        if str(column_type) == "object":
            try:
                # Case for datetime data
                df["new_datetime_column"] = pd.to_datetime(df[original_column_name])

                # Plot the datetime for pairplot as categorical data for now
                df.drop("new_datetime_column", axis=1, inplace=True)
            except ValueError:
                # Case for categorical data

                if df[original_column_name].isnull().values.any():
                    # Fill categorical missing values with mode
                    df[original_column_name].fillna(
                        df[original_column_name].mode()[0], inplace=True
                    )

                pub.sendMessage(
                    "LOG_MESSAGE", log_message="{}Encoding...".format(_spacing)
                )

                try:
                    # Clean categorical data
                    new_column_name = original_column_name + "_code"
                    df[new_column_name] = label.fit_transform(
                        df[original_column_name]
                    )
                    encoding_drop_columns.append(original_column_name)

                except (ValueError, TypeError) as e:
                    encoding_drop_columns.append(original_column_name)
                    _message = "{}Column [{}] droped <--".format(
                        _spacing, original_column_name
                    )
                    pub.sendMessage("LOG_MESSAGE", log_message=_message)

                pub.sendMessage(
                    "LOG_MESSAGE", log_message="{}Finished".format(_spacing)
                )
        else:
            if df[original_column_name].isnull().values.any():
                # Fill numerical missing values with median
                df[original_column_name].fillna(
                    df[original_column_name].median(), inplace=True
                )

    # Drop all the original categorical data columns
    if encoding_drop_columns:
        df.drop(encoding_drop_columns, axis=1, inplace=True)

    return df