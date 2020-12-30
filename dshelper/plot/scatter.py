import sys

import wx

import pandas as pd
import numpy as np
from numpy import arange, sin, pi

from pubsub import pub

import matplotlib
if 'linux' not in sys.platform:
    matplotlib.use("WXAgg")

try:
    import seaborn as sns
    sns.set()
except ImportError:
    pass

# import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure


class ScatterPanel(wx.Panel):
    """
    A panel displays the scatter plot for any given column

    Args:
        df --> pandas dataframe: passed internally for plotting

    Returns: None
    """

    def __init__(self, parent, df=None):
        wx.Panel.__init__(self, parent)

        self.df = df
        self.available_columns = list(self.df.columns)

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.toolbar = NavigationToolbar(self.canvas)

        # Drop-down select boxes
        self.text_y_axis = wx.StaticText(self, label="Y Axis:")
        self.text_x_axis = wx.StaticText(self, label="X Axis:")
        self.column_x = wx.ComboBox(
            self, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.column_y = wx.ComboBox(
            self, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.Bind(wx.EVT_COMBOBOX, self.column_selected)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.text_x_axis, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.column_x, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.text_y_axis, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.column_y, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.toolbar, 0, wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(button_sizer)
        self.SetSizer(sizer)
        self.Fit()

        pub.subscribe(self.update_available_column, "UPDATE_DISPLAYED_COLUMNS")

    def column_selected(self, event):
        """
        Function responses to select column from dropdown menu.
        It only triggers plot when both columns are selected from the dropdown menu
        """

        selected_column_id_x = self.column_x.GetCurrentSelection()
        selcted_column_x = self.available_columns[selected_column_id_x]

        selected_column_id_y = self.column_y.GetCurrentSelection()
        selcted_column_y = self.available_columns[selected_column_id_y]

        if selected_column_id_x > 0 and selected_column_id_y > 0:
            self.draw_scatter(
                selcted_column_x,
                selcted_column_y,
                self.df[selcted_column_x],
                self.df[selcted_column_y],
            )

    def draw_scatter(self, column_x, column_y, data_x, data_y):
        """
        Function that draws plot in the panel.

        Args:
            column_x --> string: column header for x axis
            column_y --> string: column header for y axis
            data_x --> 1D dataframe: dataframe column extracted from df
                (i.e. data_x = df[column_x]) as x axis data
            data_y --> 1D dataframe: dataframe column extracted from df
                (i.e. data_y = df[column_y]) as y axis data

        Returns: None
        """

        # Reset plot forst
        self.axes.clear()

        try:
            self.axes.plot(data_x, data_y, "o")
        except ValueError as e:
            # log action
            _log_message = "\nScatter plot failed due to error:\n--> {}".format(e)
            pub.sendMessage("LOG_MESSAGE", log_message=_log_message)

        # Set plot style
        self.axes.set_title("Scatter Plot for {} and {}".format(column_x, column_y))
        self.axes.set_ylabel(column_y)
        self.axes.set_xlabel(column_x)
        self.canvas.draw()

    def update_available_column(self, available_columns):
        """
        Update datafram used for plotting.

        Args:
            available_columns --> list: a list of available column headers

        Returns: None
        """

        self.available_columns = available_columns
        self.column_x.Clear()
        self.column_y.Clear()
        for column in self.available_columns:
            self.column_x.Append(column)
            self.column_y.Append(column)
