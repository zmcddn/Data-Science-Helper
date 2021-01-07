import sys

import pandas as pd

from pubsub import pub

import matplotlib
if "linux" not in sys.platform:
    matplotlib.use("WXAgg")

try:
    import seaborn as sns
    sns.set()
except ImportError:
    pass

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

    Args:
        df --> pandas dataframe: raw data frame

    Returns:
        df --> pandas dataframe: data frame cleaned with encoded categorical data and without any null data
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

                except (ValueError, TypeError):
                    encoding_drop_columns.append(original_column_name)
                    _message = "{}Column [{}] dropped <--".format(
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


def make_pair_plot(figure, df, column_name, available_columns):

    # Reset plot, clean the axes
    figure.clf()

    legend_labels = df[column_name].unique()
    legend_title = column_name

    if str(df[column_name].dtype) == "object":
        # Update hue column for categorical data
        column_name += "_code"

    df = prepare_data(df[available_columns])

    pub.sendMessage("LOG_MESSAGE", log_message="\nReady to plot...")

    try:
        # Produce pairplot using seaborn
        pair_plot = sns.pairplot(
            df,
            hue=column_name,
            palette="deep",
            size=1.2,
            diag_kind="kde",
            diag_kws=dict(shade=True),
            plot_kws=dict(s=10),
        )

        # Get the number of rows and columns from the seaborn pairplot
        pp_rows = len(pair_plot.axes)
        pp_cols = len(pair_plot.axes[0])

        # Update axes to the corresponding number of subplots from pairplot
        axes = figure.subplots(pp_rows, pp_cols)

        # Get the label and plotting order
        x_labels, y_labels = [], []
        for ax in pair_plot.axes[-1, :]:
            xlabel = ax.xaxis.get_label_text()
            x_labels.append(xlabel)
        for ax in pair_plot.axes[:, 0]:
            ylabel = ax.yaxis.get_label_text()
            y_labels.append(ylabel)

        # Setup hue for plots
        hue_values = df[column_name].unique()
        palette = sns.color_palette("muted") # get seaborn default colors
        legend_color = palette.as_hex()

        # Mimic how seaborn produce the pairplot using matplotlib subplots
        for i in range(len(x_labels)):
            for j in range(len(y_labels)):
                if i != j:
                    # Non-diagonal locations, scatter plot
                    for num, value in enumerate(hue_values):
                        sns.regplot(
                            x=df[x_labels[i]][df[column_name] == value],
                            y=df[y_labels[j]][df[column_name] == value],
                            data=df,
                            scatter=True,
                            fit_reg=False,
                            ax=axes[j, i],
                            scatter_kws={
                                's':10, # Set dot size
                                'facecolor':legend_color[num], # Set dot color
                            }
                        )
                else:
                    # Diagonal locations, distribution plot
                    for num, value in enumerate(hue_values):
                        sns.kdeplot(
                            df[x_labels[i]][df[column_name] == value],
                            ax=axes[j, i],
                            color=legend_color[num],
                            legend=False,
                            shade=True,
                        )

                # Set plot labels, only set the outter plots to avoid
                # label overlapping
                if i == 0:
                    if j == len(x_labels) - 1:
                        # Case for bottom left corner
                        axes[j, i].set_xlabel(x_labels[i], fontsize=8)
                    else:
                        axes[j, i].set_xlabel("")
                        axes[j, i].set_xticklabels([]) # Turn off tick labels
                    axes[j, i].set_ylabel(y_labels[j], fontsize=8)
                elif j == len(x_labels) - 1:
                    axes[j, i].set_xlabel(x_labels[i], fontsize=8)
                    axes[j, i].set_ylabel("")
                    axes[j, i].set_yticklabels([]) # Turn off tick labels
                else:
                    # Hide labels
                    axes[j, i].set_xlabel("")
                    axes[j, i].set_ylabel("")

                    # Turn off tick labels
                    axes[j, i].set_xticklabels([])
                    axes[j, i].set_yticklabels([])

        end_message = "Pair plots finished"
        pub.sendMessage("LOG_MESSAGE", log_message=end_message)

        handles, _ = axes[0,0].get_legend_handles_labels()
        figure.legend(
            handles,
            labels=legend_labels,
            title=legend_title,
            loc='center right',
        )

        figure.subplots_adjust(
            left=0.03,  # the left side of the subplots of the figure
            bottom=0.08,  # the bottom of the subplots of the figure
            right=0.93,  # the right side of the subplots of the figure
            top=0.97,  # the top of the subplots of the figure
            wspace=0.12,  # the amount of width reserved for space between subplots
            hspace=0.12,  # the amount of height reserved for space between subplots
        )

    except ValueError as e:
        # log Error
        _log_message = "\nPair plots failed due to error:\n--> {}".format(e)
        pub.sendMessage("LOG_MESSAGE", log_message=_log_message)
