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
        # Reset plot forst
        self.axes.clear()

        start_message = "\nPrepare to plot pair plots ..."
        pub.sendMessage("LOG_MESSAGE", log_message=start_message)
        _spacing = " " * 6

        df = self.df[self.available_columns]
        label = LabelEncoder()

        for num, column_type in enumerate(df.dtypes):
            if str(column_type) == "object":
                original_column_name = self.df.columns[num]
                _message = "--> Process encoder on column: {}".format(
                    original_column_name
                )
                pub.sendMessage("LOG_MESSAGE", log_message=_message)

                try:
                    # Clean categorical data
                    new_column_name = original_column_name + "_code"
                    df[new_column_name] = label.fit_transform(df[original_column_name])
                    df.drop(original_column_name, axis=1, inplace=True)

                except (ValueError, TypeError) as e:
                    df.drop(original_column_name, axis=1, inplace=True)
                    _message = "{}Column [{}] droped <--".format(
                        _spacing, original_column_name
                    )
                    pub.sendMessage("LOG_MESSAGE", log_message=_message)

                pub.sendMessage(
                    "LOG_MESSAGE", log_message="{}Finished".format(_spacing)
                )

        pair_plot = sns.pairplot(
            df,
            hue=column_name,
            palette="deep",
            size=1.2,
            diag_kind="kde",
            diag_kws=dict(shade=True),
            plot_kws=dict(s=10),
        )
        pair_plot.set(xticklabels=[])

        self.canvas.Destroy()
        pp_rows = len(pair_plot.axes)
        pp_cols = len(pair_plot.axes[0])
        self.figure, self.axes = plt.subplots(pp_rows, pp_cols)

        xlabels, ylabels = [], []
        for ax in pair_plot.axes[-1, :]:
            xlabel = ax.xaxis.get_label_text()
            xlabels.append(xlabel)
        for ax in pair_plot.axes[:, 0]:
            ylabel = ax.yaxis.get_label_text()
            ylabels.append(ylabel)

        for i in range(len(xlabels)):
            for j in range(len(ylabels)):
                if i != j:
                    sns.regplot(
                        x=xlabels[i],
                        y=ylabels[j],
                        data=df,
                        scatter=True,
                        fit_reg=False,
                        ax=self.axes[j, i],
                    )
                else:
                    sns.kdeplot(df[xlabels[i]], ax=self.axes[j, i])

        self.canvas = FigureCanvas(self, -1, self.figure)

        end_message = "Pair plots finished"
        pub.sendMessage("LOG_MESSAGE", log_message=end_message)

        self.canvas.draw()

    def update_available_column(self, available_columns):
        self.available_columns = available_columns
        self.dropdown_menu.Clear()
        for column in self.available_columns:
            self.dropdown_menu.Append(column)
