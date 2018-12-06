import wx

import pandas as pd
import numpy as np
from numpy import arange, sin, pi

from wx.lib.pubsub import pub

import matplotlib
matplotlib.use("WXAgg")

try:
    import seaborn as sns
    sns.set()
except ImportError:
    pass

# import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.figure import Figure
import matplotlib.cm as cm



class BoxViolinPanel(wx.Panel):
    """
    A panel displays the box plot and violin for any given column
    """

    def __init__(self, parent, df=None):
        wx.Panel.__init__(self, parent)

        self.df = df
        self.available_columns = list(self.df.columns)

        self.splitter = wx.SplitterWindow(self, wx.ID_ANY)
        self.box_panel = wx.Panel(self.splitter, 1)
        self.violin_panel = wx.Panel(self.splitter, 1)
        self.splitter.SplitVertically(self.box_panel, self.violin_panel)
        self.splitter.SetSashGravity(0.5)  # Set proportion for the splitter window

        self.buttonpanel = wx.Panel(self, 1)  # Panel contains all the buttons
        self.buttonpanel.SetBackgroundColour("white")

        self.box_figure = Figure()
        self.box_axes = self.box_figure.add_subplot(111)
        self.box_canvas = FigureCanvas(self.box_panel, -1, self.box_figure)
        self.box_color_bar = None  # Flag for color bar
        self.box_toolbar = NavigationToolbar(self.box_canvas)

        self.violin_figure = Figure()
        self.violin_axes = self.violin_figure.add_subplot(111)
        self.violin_canvas = FigureCanvas(self.violin_panel, -1, self.violin_figure)
        self.violin_color_bar = None  # Flag for color bar
        self.violin_toolbar = NavigationToolbar(self.violin_canvas)

        # Drop-down select boxes
        self.text_y_axis = wx.StaticText(self.buttonpanel, label='Y Axis:')
        self.text_x_axis = wx.StaticText(self.buttonpanel, label='X Axis:')
        self.column1 = wx.ComboBox(
            self.buttonpanel, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.column2 = wx.ComboBox(
            self.buttonpanel, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.Bind(wx.EVT_COMBOBOX, self.column_selected)

        # Box plot layout
        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(self.box_canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        box_sizer.Add(self.box_toolbar, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.box_panel.SetSizer(box_sizer)

        # Violin plot layout
        violin_sizer = wx.BoxSizer(wx.VERTICAL)
        violin_sizer.Add(self.violin_canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        violin_sizer.Add(self.violin_toolbar, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.violin_panel.SetSizer(violin_sizer)

        # Bottom button bar layout
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.text_x_axis, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.column1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.text_y_axis, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.column2, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.buttonpanel.SetSizer(button_sizer)

        # Main panel layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL)
        sizer.Add(self.buttonpanel)
        self.SetSizer(sizer)
        self.Fit()

        pub.subscribe(self.update_available_column, "UPDATE_DISPLAYED_COLUMNS")

    def column_selected(self, event):
        selected_column_id_1 = self.column1.GetCurrentSelection()
        selcted_column_1 = self.available_columns[selected_column_id_1]

        selected_column_id_2 = self.column2.GetCurrentSelection()
        selcted_column_2 = self.available_columns[selected_column_id_2]

        if selected_column_id_1 > 0 and selected_column_id_2 > 0:
            self.draw_plots(
                selcted_column_1,
                selcted_column_2,
                self.df[selcted_column_1],
                self.df[selcted_column_2],
            )

    def draw_plots(self, column1, column2, data1, data2):
        pass
        # # Reset plot first
        # self.axes.clear()

        # if self.color_bar:
        #     self.color_bar.remove()

        # # Set plot style
        # self.axes.set_title("Heat Map Plot for {} and {}".format(column1, column2))
        # self.axes.set_ylabel(column2)
        # self.axes.set_xlabel(column1)
        # self.color_bar = self.figure.colorbar(im, ax=self.axes)
        # self.canvas.draw()

    def update_available_column(self, available_columns):
        self.available_columns = available_columns
        self.column1.Clear()
        self.column2.Clear()
        for column in self.available_columns:
            self.column1.Append(column)
            self.column2.Append(column)
