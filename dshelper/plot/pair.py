import sys

import wx

import pandas as pd
import numpy as np
from numpy import arange, sin, pi

from wx.lib.pubsub import pub

import matplotlib
if "linux" not in sys.platform:
    matplotlib.use("WXAgg")

try:
    import seaborn as sns
    sns.set()
except ImportError:
    pass

from sklearn.preprocessing import LabelEncoder

# import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class PairPanel(wx.Panel):
    """
    A panel displays the pair plots for any given column
    """

    def __init__(self, parent, df=None):
        wx.Panel.__init__(self, parent)

        self.df = df
        self.available_columns = list(self.df.columns)

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.toolbar = NavigationToolbar(self.canvas)

        self.text_hue = wx.StaticText(self, label="Hue:")
        self.dropdown_menu = wx.ComboBox(
            self, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.Bind(wx.EVT_COMBOBOX, self.column_selected)

        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        toolbar_sizer.Add(self.text_hue, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        toolbar_sizer.Add(self.dropdown_menu, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        toolbar_sizer.Add(self.toolbar, 0, wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(toolbar_sizer)
        self.SetSizer(sizer)
        self.Fit()

        pub.subscribe(self.update_available_column, "UPDATE_DISPLAYED_COLUMNS")

    def column_selected(self, event):
        selected_column_id = self.dropdown_menu.GetCurrentSelection()
        selcted_column = self.available_columns[selected_column_id]

        self.draw_pair(selcted_column)

    def draw_pair(self, column_name):
        """
        Seaborn pairplot return a series of subplots within one figure,
        therefore it is really difficult to plot it directly in the existing 
        figure. Instead, we mimic how it is plotted and add corresponding 
        number of matplotlib subplots and plot the pairplot inside the 
        matplotlib subplots
        """

        # Reset plot, clean the axes
        self.figure.clf()

        start_message = "\nPrepare to plot pair plots ..."
        pub.sendMessage("LOG_MESSAGE", log_message=start_message)
        _spacing = " " * 7

        df = self.df[self.available_columns]
        label = LabelEncoder()

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

        pub.sendMessage("LOG_MESSAGE", log_message="\nReady to plot...")

        # Produce pairpolot using seaborn
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
        self.axes = self.figure.subplots(pp_rows, pp_cols)

        # Get the label and plotting order
        xlabels, ylabels = [], []
        for ax in pair_plot.axes[-1, :]:
            xlabel = ax.xaxis.get_label_text()
            xlabels.append(xlabel)
        for ax in pair_plot.axes[:, 0]:
            ylabel = ax.yaxis.get_label_text()
            ylabels.append(ylabel)

        # Mimic how seaborn produce the pairplot using matplotlib subplots
        for i in range(len(xlabels)):
            for j in range(len(ylabels)):
                if i != j:
                    # Non-diagnal locations, scatter plot
                    sns.regplot(
                        x=xlabels[i],
                        y=ylabels[j],
                        data=df,
                        scatter=True,
                        fit_reg=False,
                        ax=self.axes[j, i],
                    )
                else:
                    # Diagnal locations, distribution plot
                    sns.kdeplot(df[xlabels[i]], ax=self.axes[j, i], legend=False)

                # Set plot labels, only set the outter plots to avoid label overlapping
                if i == 0:
                    if j == len(xlabels) - 1:
                        # Case for bottom left corner
                        self.axes[j, i].set_xlabel(xlabels[i], fontsize=8)
                    else:
                        self.axes[j, i].set_xlabel("")
                        self.axes[j, i].set_xticklabels([]) # Turn off tick labels
                    self.axes[j, i].set_ylabel(ylabels[j], fontsize=8)
                elif j == len(xlabels) - 1:
                    self.axes[j, i].set_xlabel(xlabels[i], fontsize=8)
                    self.axes[j, i].set_ylabel("")
                    self.axes[j, i].set_yticklabels([]) # Turn off tick labels
                else:
                    # Hide labels
                    self.axes[j, i].set_xlabel("")
                    self.axes[j, i].set_ylabel("")

                    # Turn off tick labels
                    self.axes[j, i].set_xticklabels([])
                    self.axes[j, i].set_yticklabels([])

        end_message = "Pair plots finished"
        pub.sendMessage("LOG_MESSAGE", log_message=end_message)

        self.figure.subplots_adjust(
            left=0.03, # the left side of the subplots of the figure
            bottom=0.08, # the bottom of the subplots of the figure
            right=0.99, # the right side of the subplots of the figure
            top=0.97,   # the top of the subplots of the figure
            wspace=0.12, # the amount of width reserved for space between subplots
            hspace=0.12, # the amount of height reserved for space between subplots
        )

        self.canvas.draw()
        self.Refresh()

    def update_available_column(self, available_columns):
        self.available_columns = available_columns
        self.dropdown_menu.Clear()
        for column in self.available_columns:
            self.dropdown_menu.Append(column)
