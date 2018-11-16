import wx

import pandas as pd
import numpy as np
from numpy import arange, sin, pi

import matplotlib

# import seaborn as sns

matplotlib.use("WXAgg")

# import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure


class HistPanel(wx.Panel):
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

    def column_selected(self, event):
        selected_column_id = self.dropdown_menu.GetCurrentSelection()
        selcted_column = self.available_columns[selected_column_id]

        self.draw_hist(selcted_column, self.df[selcted_column])

    def draw_hist(self, column_name, data):
        # Reset plot forst
        self.axes.clear()

        # Check data type
        if data.dtype == "object":
            # Different drawing method for strings
            value_count = data.value_counts().sort_index()
            value_count.plot(kind='bar', ax=self.axes)
        else:
            self.axes.hist(data.dropna(), bins=100)

        # Set plot info
        self.axes.set_title("Histogram Plot for %s" % column_name)
        self.axes.set_ylabel("Value Count")
        self.canvas.draw()


if __name__ == "__main__":
    # Test for indivial panel layout
    app = wx.App(0)
    frame = wx.Frame(None, wx.ID_ANY)
    fa = HistPanel(frame)
    frame.Show()
    app.MainLoop()
