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
    import seaborn
    seaborn.set()
except ImportError:
    pass

# import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure


class HistPanel(wx.Panel):
    """
    A panel displays the histogram plot for any given column

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

        self.dropdown_menu = wx.ComboBox(
            self, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.Bind(wx.EVT_COMBOBOX, self.column_selected)

        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
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
        selected_column = self.available_columns[selected_column_id]

        self.draw_hist(selected_column, self.df[selected_column])

    def draw_hist(self, column_name, data):
        """
        Function that draws plot in the panel.

        Args:
            column_name --> string: the name of the column that needs to
                be drawn
            data --> 1D dataframe: dataframe column extracted from df
                (i.e. data = df[column_name])

        Returns: None
        """

        # Reset plot first
        self.axes.clear()

        try:
            # Check data type
            if data.dtype == "object":
                # Different drawing method for strings
                value_count = data.value_counts().sort_index()
                value_count.plot(kind="bar", ax=self.axes)
            else:
                self.axes.hist(data.dropna(), bins=100)
        except ValueError as e:
            # log Error
            _log_message = "\nHistogram plot failed due to error:\n--> {}".format(e)
            pub.sendMessage("LOG_MESSAGE", log_message=_log_message)

        # Set plot info
        self.axes.set_title("Histogram Plot for %s" % column_name)
        self.axes.set_ylabel("Value Count")
        self.canvas.draw()

    def update_available_column(self, available_columns):
        """
        Update dataframe used for plotting.

        Args:
            available_columns --> list: a list of available column headers

        Returns: None
        """

        self.available_columns = available_columns
        self.dropdown_menu.Clear()
        for column in self.available_columns:
            self.dropdown_menu.Append(column)


if __name__ == "__main__":
    # Test for individual panel layout
    app = wx.App(0)
    frame = wx.Frame(None, wx.ID_ANY)
    fa = HistPanel(frame)
    frame.Show()
    app.MainLoop()
