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
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.figure import Figure
import matplotlib.cm as cm



class BoxViolinPanel(wx.Panel):
    """
    A panel displays the box plot and violin for any given column

    Args:
        df --> pandas dataframe: passed internally for plotting

    Returns: None
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
        self.box_toolbar = NavigationToolbar(self.box_canvas)

        self.violin_figure = Figure()
        self.violin_axes = self.violin_figure.add_subplot(111)
        self.violin_canvas = FigureCanvas(self.violin_panel, -1, self.violin_figure)
        self.violin_toolbar = NavigationToolbar(self.violin_canvas)

        # Drop-down select boxes
        self.text_y_axis = wx.StaticText(self.buttonpanel, label='Y Axis:')
        self.text_x_axis = wx.StaticText(self.buttonpanel, label='X Axis:')
        self.text_hue = wx.StaticText(self.buttonpanel, label='Hue:')
        self.column_x = wx.ComboBox(
            self.buttonpanel, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.column_y = wx.ComboBox(
            self.buttonpanel, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.column_hue = wx.ComboBox(
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
        button_sizer.Add(self.column_x, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.text_y_axis, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.column_y, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.text_hue, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.column_hue, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.buttonpanel.SetSizer(button_sizer)

        # Main panel layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL)
        sizer.Add(self.buttonpanel)
        self.SetSizer(sizer)
        self.Fit()

        pub.subscribe(self.update_available_column, "UPDATE_DISPLAYED_COLUMNS")

    def column_selected(self, event):
        """
        Function responses to select column from dropdown menu.
        The plot is only triggered when all three columns are selected in the
        dropdown list
        """

        selected_column_id_x = self.column_x.GetCurrentSelection()
        selcted_column_x = self.available_columns[selected_column_id_x]

        selected_column_id_y = self.column_y.GetCurrentSelection()
        selcted_column_y = self.available_columns[selected_column_id_y]

        selected_column_id_hue = self.column_hue.GetCurrentSelection()
        selcted_column_hue = self.available_columns[selected_column_id_hue]

        if selected_column_id_x > 0 and selected_column_id_y > 0 and selected_column_id_hue > 0:
            self.draw_plots(
                selcted_column_x,
                selcted_column_y,
                selcted_column_hue,
            )

    def draw_plots(self, column_x, column_y, column_hue):
        """
        Function that draws plot in the panel.

        Args:
            column_x --> 1D dataframe: dataframe column extracted from df
                (i.e. column_x = df[column_x_name]) as x axis data
            column_y --> 1D dataframe: dataframe column extracted from df
                (i.e. column_y = df[column_y_name]) as y axis data
            column_hue --> 1D dataframe: dataframe column extracted from df
                (i.e. column_hue = df[column_hue_name]) as legend data

        Returns: None
        """

        # Reset plot first
        self.box_axes.clear()
        self.violin_axes.clear()

        # Box plot
        try:
            sns.boxplot(x=column_x, y=column_y, hue=column_hue, data=self.df, ax=self.box_axes)
        except ValueError as e:
            # log Error
            _log_message = "\nBox plot failed due to error:\n--> {}".format(e)
            pub.sendMessage("LOG_MESSAGE", log_message=_log_message)

        # Violin plot
        try:
            sns.violinplot(x=column_x, y=column_y, hue=column_hue, data=self.df, split=True, ax=self.violin_axes)
        except ValueError as e:
            # log Error
            _log_message = "\nVolin plot failed due to error:\n--> {}".format(e)
            pub.sendMessage("LOG_MESSAGE", log_message=_log_message)

        # Set plot style
        self.box_axes.set_title("Box Plot for {} and {}".format(column_x, column_y))
        self.box_axes.set_ylabel(column_y)
        self.box_axes.set_xlabel(column_x)
        self.box_canvas.draw()

        self.violin_axes.set_title("Violin Plot for {} and {}".format(column_x, column_y))
        self.violin_axes.set_ylabel(column_y)
        self.violin_axes.set_xlabel(column_x)
        self.violin_canvas.draw()

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
        self.column_hue.Clear()
        for column in self.available_columns:
            self.column_x.Append(column)
            self.column_y.Append(column)
            self.column_hue.Append(column)
