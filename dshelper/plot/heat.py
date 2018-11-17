import wx

import pandas as pd
import numpy as np
from numpy import arange, sin, pi

from wx.lib.pubsub import pub

import matplotlib
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


class HeatPanel(wx.Panel):
    """
    A panel displays the histogram plot for any given column
    """

    def __init__(self, parent, df=None):
        wx.Panel.__init__(self, parent)

        self.df = df
        self.available_columns = list(self.df.columns)

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.toolbar = NavigationToolbar(self.canvas)

        self.column1 = wx.ComboBox(
            self, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.column2 = wx.ComboBox(
            self, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.Bind(wx.EVT_COMBOBOX, self.column_selected)

        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        toolbar_sizer.Add(self.column1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        toolbar_sizer.Add(self.column2, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        toolbar_sizer.Add(self.toolbar, 0, wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(toolbar_sizer)
        self.SetSizer(sizer)
        self.Fit()

        pub.subscribe(self.update_available_column, "UPDATE_DISPLAYED_COLUMNS")

    def column_selected(self, event):
        selected_column_id_1 = self.column1.GetCurrentSelection()
        selcted_column_1 = self.available_columns[selected_column_id_1]

        selected_column_id_2 = self.column2.GetCurrentSelection()
        selcted_column_2 = self.available_columns[selected_column_id_2]

        if selcted_column_1 and selcted_column_2:
            self.draw_heat(selcted_column_1, selcted_column_2, self.df[selcted_column_1], self.df[selcted_column_2])

    def draw_heat(self, column1, column2, data1, data2):
        # Reset plot first
        self.axes.clear()

        # # Check data type
        # if data.dtype == "object":
        #     # Different drawing method for strings
        #     value_count = data.value_counts().sort_index()
        #     value_count.plot(kind="bar", ax=self.axes)
        # else:
        self.axes.hist2d(data1.dropna(), data2.dropna())

        # Set plot info
        self.axes.set_title("Heat Map Plot for {} and {}".format(column1, column2))
        # self.axes.set_ylabel("Value Count")
        self.canvas.draw()

    def update_available_column(self, available_columns):
        self.available_columns = available_columns
        self.column1.Clear()
        self.column2.Clear()
        for column in self.available_columns:
            self.column1.Append(column)
            self.column2.Append(column)
