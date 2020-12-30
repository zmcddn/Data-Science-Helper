import sys

import wx

import pandas as pd
import numpy as np
from numpy import arange, sin, pi

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

# import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from .utils import prepare_data


class PairPanel(wx.Panel):
    """
    A panel displays the pair plots for any given column

    Args:
        df --> pandas dataframe: passed internally for plotting

    Returns: None
    """

    def __init__(self, parent, df=None):
        wx.Panel.__init__(self, parent)

        self.df = df
        self.available_columns = list(self.df.columns)
        self.hue_columns = self._get_hue_column()

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.toolbar = NavigationToolbar(self.canvas)

        self.text_hue = wx.StaticText(self, label="Hue:")
        self.dropdown_menu = wx.ComboBox(
            self, choices=self.hue_columns, style=wx.CB_READONLY
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
        """
        Function responses to select column from dropdown menu.
        """

        selected_column_id = self.dropdown_menu.GetCurrentSelection()
        selcted_column = self.hue_columns[selected_column_id]

        self.draw_pair(selcted_column)

    def draw_pair(self, column_name):
        """
        Function that draws plot in the panel.

        Note:
            Seaborn pairplot return a series of subplots within one figure,
            therefore it is really difficult to plot it directly in the
            existing figure.
            Instead, we mimic how it is plotted and add corresponding
            number of matplotlib subplots and plot the pairplot inside the
            matplotlib subplots

        Args:
            column_name --> string: the name of the column that needs to
                be drawn
        Returns: None
        """

        # Reset plot, clean the axes
        self.figure.clf()

        legend_labels = self.df[column_name].unique()
        legend_title = column_name

        df = prepare_data(self.df[self.available_columns])

        if str(self.df[column_name].dtype) == "object":
            # Update hue column for categorical data
            column_name += "_code"

        pub.sendMessage("LOG_MESSAGE", log_message="\nReady to plot...")

        try:
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

            # Setup hue for plots
            hue_values = df[column_name].unique()
            palette = sns.color_palette("muted") # get seaborn default colors
            legend_color = palette.as_hex()

            # Mimic how seaborn produce the pairplot using matplotlib subplots
            for i in range(len(xlabels)):
                for j in range(len(ylabels)):
                    if i != j:
                        # Non-diagnal locations, scatter plot
                        for num, value in enumerate(hue_values):
                            sns.regplot(
                                x=df[xlabels[i]][df[column_name] == value],
                                y=df[ylabels[j]][df[column_name] == value],
                                data=df,
                                scatter=True,
                                fit_reg=False,
                                ax=self.axes[j, i],
                                scatter_kws={
                                    's':10, # Set dot size
                                    'facecolor':legend_color[num], # Set dot color
                                }
                            )
                    else:
                        # Diagnal locations, distribution plot
                        for num, value in enumerate(hue_values):
                            sns.kdeplot(
                                df[xlabels[i]][df[column_name] == value],
                                ax=self.axes[j, i],
                                color=legend_color[num],
                                legend=False,
                                shade=True,
                            )

                    # Set plot labels, only set the outter plots to avoid
                    # label overlapping
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

            handles, _ = self.axes[0,0].get_legend_handles_labels()
            self.figure.legend(
                handles,
                labels=legend_labels,
                title=legend_title,
                loc='center right',
            )

            self.figure.subplots_adjust(
                left=0.03, # the left side of the subplots of the figure
                bottom=0.08, # the bottom of the subplots of the figure
                right=0.93, # the right side of the subplots of the figure
                top=0.97,   # the top of the subplots of the figure
                wspace=0.12, # the amount of width reserved for space between subplots
                hspace=0.12, # the amount of height reserved for space between subplots
            )

        except ValueError as e:
            # log Error
            _log_message = "\nPair plots failed due to error:\n--> {}".format(e)
            pub.sendMessage("LOG_MESSAGE", log_message=_log_message)

        self.canvas.draw()
        self.Refresh()

    def _get_hue_column(self):
        """
        This internal function limits the available columns for hue selection.
        It filters out those columns with too many dinstinct values.

        Currently it is set for the number 6, which is the number of distinct
        colors for the default seaborn color palette.

        Args: None

        Returns:
            hue_columns --> list: a list of column headers
        """

        hue_columns = []
        for column in self.available_columns:
            if self.df[column].nunique() <= 6:
                # Restrict hue selection based on distinct values in column
                hue_columns.append(column)

        return hue_columns

    def update_available_column(self, available_columns):
        """
        Update datafram used for plotting.

        Args:
            available_columns --> list: a list of available column headers

        Returns: None
        """

        self.available_columns = available_columns

        # Update hue column selection
        self.hue_columns = self._get_hue_column()

        # Update dropdown menu
        self.dropdown_menu.Clear()
        for column in self.hue_columns:
            self.dropdown_menu.Append(column)
