#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dshelper is a GUI for visualization of pandas dataframes. 
In addition, it provides some functionalities in helping with some exploratory analysis and examination of raw data

Copyright (c) 2018 - 2019, Minchang (Carson) Zhang.
License: MIT (see LICENSE for details)
"""

import datetime

import pandas as pd
import numpy as np

import wx
import wx.grid
from wx.lib.pubsub import pub

from data.data_panel import DataTablePanel, DataDescribePanel, ColumnSelectionPanel
from plot.plot_panel import PlotPanel

EVEN_ROW_COLOUR = "#CCE6FF"
ODD_ROW_COLOUR = "#F0F8FF"
GRID_LINE_COLOUR = "#D3D3D3"


def get_df():
    # # Test dataframe
    # todays_date = datetime.datetime.now().date()
    # index = pd.date_range(
    #     todays_date - datetime.timedelta(10), periods=10, freq="D"
    # )
    # df = pd.DataFrame(index=index, columns=list(range(30)))
    # df = df.fillna(500)
    # # df.reset_index(inplace=True)
    # # df = pd.DataFrame(np.random.random((10, 5)))

    df = pd.read_csv("./titanic_data/train.csv")

    # Insert some random dates into the df
    random_dates = [
        datetime.date(2016, 1, 1) + datetime.timedelta(days=int(days))
        for days in np.random.randint(1, 50, df.shape[0])
    ]
    # Insert to df
    df.insert(0, "Random Date", random_dates)

    return df


class LogPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)

        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        self.log = wx.TextCtrl(self, style=style)
        self.log.SetBackgroundColour("#D5F5E3")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.log, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        self.log.write(
            "Log begins here at time: {:%d, %b %Y, %H:%M}\n".format(
                datetime.datetime.now()
            )
        )
        self.log.write("wxPython version: {}\n".format(wx.__version__))

        pub.subscribe(self.PrintMessage, "LOG_MESSAGE")

    def PrintMessage(self, log_message):
        self.log.write(log_message)
        self.log.write("\n")


class DFSplitterPanel(wx.Panel):
    """
    A top and bottom splitter panel to display dataframe data and summary (i.e. df.describe)
    """

    def __init__(self, parent, df=None):
        wx.Panel.__init__(self, parent)

        self.df = df

        splitter = wx.SplitterWindow(
            self, style=wx.SP_NOBORDER | wx.SP_3DSASH | wx.SP_LIVE_UPDATE
        )
        topPanel = wx.Panel(splitter)
        bottomPanel = wx.Panel(splitter)
        topPanel.SetBackgroundColour("#AED6F1")
        bottomPanel.SetBackgroundColour("#F9E79F")

        # Create a notebook for the top panel (data panel)
        # each page serves a different function
        data_notebook = wx.Notebook(topPanel)
        self.raw_data_page = DataTablePanel(data_notebook, -1, df=self.df)
        self.plot_page = PlotPanel(data_notebook, df=self.df)
        self.raw_data_page.SetBackgroundColour("WHITE")
        self.plot_page.SetBackgroundColour("YELLOW")

        # Add pages into the notebook for display
        data_notebook.AddPage(self.raw_data_page, "Raw Data")
        data_notebook.AddPage(self.plot_page, "Plot")

        # Put the notebook in a sizer in the panel for layout
        sizer = wx.BoxSizer()
        sizer.Add(data_notebook, 1, wx.EXPAND | wx.SP_NOBORDER)
        topPanel.SetSizer(sizer)

        self.data_describe = DataDescribePanel(bottomPanel, -1, df=self.df)
        bottom_sizer = wx.BoxSizer()
        bottom_sizer.Add(self.data_describe, 1, wx.EXPAND | wx.SP_NOBORDER)
        bottomPanel.SetSizer(bottom_sizer)

        # Setup splitter window and put it in a sizer for display
        splitter.SplitHorizontally(topPanel, bottomPanel)
        splitter.SetSashGravity(0.7)  # Set proportion for the splitter window
        PanelSizer = wx.BoxSizer(wx.VERTICAL)
        PanelSizer.Add(splitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(PanelSizer)


class SideSplitterPanel(wx.Panel):
    """
    A left and right splitter panel to display the dataframe and log/stats
    """

    def __init__(self, parent, df=None):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.df = df

        splitter = wx.SplitterWindow(
            self, style=wx.SP_NOBORDER | wx.SP_3DSASH | wx.SP_LIVE_UPDATE
        )
        leftPanel = DFSplitterPanel(splitter, df=self.df)
        rightPanel = wx.Panel(splitter)
        leftPanel.SetBackgroundColour("YELLOW GREEN")
        rightPanel.SetBackgroundColour("SLATE BLUE")

        # Create a notebook for the right panel (log/stat panel)
        # each page serves a different function
        data_notebook = wx.Notebook(rightPanel)
        data_notebook.SetBackgroundColour("WHITE")
        self.column_page = ColumnSelectionPanel(data_notebook, -1, df=self.df)
        self.log_page = LogPanel(data_notebook, -1)

        # Add pages into the notebook for display
        data_notebook.AddPage(self.column_page, "Column")
        data_notebook.AddPage(self.log_page, "Log")

        # Put the notebook in a sizer in the panel for layout
        sizer = wx.BoxSizer()
        sizer.Add(data_notebook, 1, wx.EXPAND | wx.SP_NOBORDER)
        rightPanel.SetSizer(sizer)

        splitter.SplitVertically(leftPanel, rightPanel)
        splitter.SetSashGravity(0.8)  # Set proportion for the splitter window
        PanelSizer = wx.BoxSizer(wx.VERTICAL)
        PanelSizer.Add(splitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(PanelSizer)


class MyStatusBar(wx.StatusBar):
    """
    Custom status bar for extra functioning bnuttons
    """

    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent)

        self.SetFieldsCount(5)
        self.SetStatusWidths([200, 200, -1, 200, 200])
        self.sizeChanged = False
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # Text fields with intial content
        self.SetStatusText("some text", 0)
        self.SetStatusText("some text", 1)
        self.SetStatusText("some text", 2)

        # Field for buttons
        self.hide_show_bottom = wx.Button(self, -1, "Hide Bottom Panel")
        self.hide_show_side = wx.Button(self, -1, "Hide Right Panel")

        # Set button styles for attention
        self.hide_show_bottom.SetForegroundColour("orange")
        self.hide_show_bottom.SetBackgroundColour("#FDE68B")  # light yellow
        self.hide_show_side.SetForegroundColour("orange")
        self.hide_show_side.SetBackgroundColour("#FDE68B")  # light yellow

        # set the initial position for buttons
        self.Reposition()

    def OnSize(self, evt):
        evt.Skip()
        self.Reposition()  # for normal size events

        # Set a flag so the idle time handler will also do the repositioning.
        # It is done this way to get around a buglet where GetFieldRect is not
        # accurate during the EVT_SIZE resulting from a frame maximize.
        self.sizeChanged = True

    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()

    # reposition the buttons
    def Reposition(self):
        rect1 = self.GetFieldRect(3)
        rect1.x += 1
        rect1.y += 1
        self.hide_show_bottom.SetRect(rect1)

        rect2 = self.GetFieldRect(4)
        rect2.x += 1
        rect2.y += 1
        self.hide_show_side.SetRect(rect2)

        self.sizeChanged = False


class MainFrame(wx.Frame):
    """
    Main frame to display all the content
    """

    def __init__(self, parent, id):
        wx.Frame.__init__(self, None, title="Data Science Helper")

        self.df = get_df()
        cols = self.df.shape[1]
        rows = self.df.shape[0]
        _memory_use = self.df.memory_usage(deep=True).sum() / 1024
        # Note that this would be equivalent to df.info(memory_usage='deep')
        if _memory_use > 1024:
            memory_usage = "{:.2f} MB".format(_memory_use / 1024)
        else:
            memory_usage = "{:.2f} KB".format(_memory_use)

        # set custom status bar
        self.status_bar = MyStatusBar(self)
        self.SetStatusBar(self.status_bar)

        self.main_splitter = SideSplitterPanel(self, df=self.df)

        self.status_bar.SetStatusText(" Rows: {}".format(rows), 0)
        self.status_bar.SetStatusText(" Columns: {}".format(cols), 1)
        self.status_bar.SetStatusText(" Memory Usage: {}".format(memory_usage), 2)

        self.Refresh()
        self.Show()
        self.Maximize(True)

        pub.subscribe(self.update_column_stat, "UPDATE_DF")

    def update_column_stat(self, df):
        # update number of columns
        cols = df.shape[1]
        self.status_bar.SetStatusText(" Columns: {}".format(cols), 1)


if __name__ == "__main__":
    app = wx.App()
    MainFrame(None, -1)
    app.MainLoop()
