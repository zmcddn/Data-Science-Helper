#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dshelper is a GUI for visualization of pandas dataframes. 
In addition, it provides some functionalities in helping with some exploratory analysis and examination of raw data

Copyright (c) 2018 - 2019, Minchang (Carson) Zhang.
License: MIT (see LICENSE for details)
"""

import datetime
import sys

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

        self.splitter = wx.SplitterWindow(
            self, style=wx.SP_NOBORDER | wx.SP_3DSASH | wx.SP_LIVE_UPDATE
        )
        self.topPanel = wx.Panel(self.splitter)
        self.bottomPanel = wx.Panel(self.splitter)
        self.topPanel.SetBackgroundColour("#AED6F1")
        self.bottomPanel.SetBackgroundColour("#F9E79F")

        # Create a notebook for the top panel (data panel)
        # each page serves a different function
        data_notebook = wx.Notebook(self.topPanel)
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
        self.topPanel.SetSizer(sizer)

        self.data_describe = DataDescribePanel(self.bottomPanel, -1, df=self.df)
        bottom_sizer = wx.BoxSizer()
        bottom_sizer.Add(self.data_describe, 1, wx.EXPAND | wx.SP_NOBORDER)
        self.bottomPanel.SetSizer(bottom_sizer)

        # Setup splitter window and put it in a sizer for display
        self.splitter.SplitHorizontally(self.topPanel, self.bottomPanel)
        self.splitter.SetSashGravity(0.7)  # Set proportion for the splitter window
        PanelSizer = wx.BoxSizer(wx.VERTICAL)
        PanelSizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(PanelSizer)

        pub.subscribe(self.hide_show_bottom_panel, "BOTTOM_PANEL")

    def hide_show_bottom_panel(self, status):
        if status == "hide":
            self.splitter.Unsplit(self.bottomPanel)

        if status == "show":
            self.splitter.SplitHorizontally(self.topPanel, self.bottomPanel)


class SideSplitterPanel(wx.Panel):
    """
    A left and right splitter panel to display the dataframe and log/stats
    """

    def __init__(self, parent, df=None):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.df = df

        self.splitter = wx.SplitterWindow(
            self, style=wx.SP_NOBORDER | wx.SP_3DSASH | wx.SP_LIVE_UPDATE
        )
        self.leftPanel = DFSplitterPanel(self.splitter, df=self.df)
        self.rightPanel = wx.Panel(self.splitter)
        self.leftPanel.SetBackgroundColour("YELLOW GREEN")
        self.rightPanel.SetBackgroundColour("SLATE BLUE")

        # Create a notebook for the right panel (log/stat panel)
        # each page serves a different function
        data_notebook = wx.Notebook(self.rightPanel)
        data_notebook.SetBackgroundColour("WHITE")
        self.column_page = ColumnSelectionPanel(data_notebook, -1, df=self.df)
        self.log_page = LogPanel(data_notebook, -1)

        # Add pages into the notebook for display
        data_notebook.AddPage(self.column_page, "Column")
        data_notebook.AddPage(self.log_page, "Log")

        # Put the notebook in a sizer in the panel for layout
        sizer = wx.BoxSizer()
        sizer.Add(data_notebook, 1, wx.EXPAND | wx.SP_NOBORDER)
        self.rightPanel.SetSizer(sizer)

        self.splitter.SplitVertically(self.leftPanel, self.rightPanel)
        self.splitter.SetSashGravity(0.8)  # Set proportion for the splitter window
        PanelSizer = wx.BoxSizer(wx.VERTICAL)
        PanelSizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(PanelSizer)

        pub.subscribe(self.hide_show_right_panel, "RIGHT_PANEL")

    def hide_show_right_panel(self, status):
        if status == "hide":
            self.splitter.Unsplit(self.rightPanel)

        if status == "show":
            self.splitter.SplitVertically(self.leftPanel, self.rightPanel)


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
        self.hide_show_bottom = wx.ToggleButton(self, -1, "Hide Bottom Panel")
        self.hide_show_side = wx.ToggleButton(self, -1, "Hide Right Panel")

        # Set button styles for attention
        self.hide_show_bottom.SetForegroundColour("orange")
        self.hide_show_bottom.SetBackgroundColour("#FDE68B")  # light yellow
        self.hide_show_side.SetForegroundColour("orange")
        self.hide_show_side.SetBackgroundColour("#FDE68B")  # light yellow

        # Button functions
        self.Bind(wx.EVT_TOGGLEBUTTON, self.hide_show_panels)

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

    def hide_show_panels(self, event):
        # Function for bottom panel
        if self.hide_show_bottom.GetValue() == True:
            # Hide bottom panel
            pub.sendMessage("BOTTOM_PANEL", status="hide")
            self.hide_show_bottom.SetLabel("Show Bottom Panel")
            self.hide_show_bottom.SetForegroundColour("blue")
            self.hide_show_bottom.SetBackgroundColour("#C8FD8B")  # light green
        elif self.hide_show_bottom.GetValue() == False:
            # Show bottom panel
            pub.sendMessage("BOTTOM_PANEL", status="show")
            self.hide_show_bottom.SetLabel("Hide Bottom Panel")
            self.hide_show_bottom.SetForegroundColour("orange")
            self.hide_show_bottom.SetBackgroundColour("#FDE68B")  # light yellow

        # Function for right panel
        if self.hide_show_side.GetValue() == True:
            # Hide bottom panel
            pub.sendMessage("RIGHT_PANEL", status="hide")
            self.hide_show_side.SetLabel("Show Right Panel")
            self.hide_show_side.SetForegroundColour("blue")
            self.hide_show_side.SetBackgroundColour("#C8FD8B")  # light green
        elif self.hide_show_side.GetValue() == False:
            # Show bottom panel
            pub.sendMessage("RIGHT_PANEL", status="show")
            self.hide_show_side.SetLabel("Hide Right Panel")
            self.hide_show_side.SetForegroundColour("orange")
            self.hide_show_side.SetBackgroundColour("#FDE68B")  # light yellow


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

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        pub.subscribe(self.update_column_stat, "UPDATE_DF")

    def update_column_stat(self, df):
        # update number of columns
        cols = df.shape[1]
        self.status_bar.SetStatusText(" Columns: {}".format(cols), 1)

    def OnCloseWindow(self, event):
        self.Destroy()
        sys.exit(0)


if __name__ == "__main__":
    app = wx.App()
    MainFrame(None, -1)
    app.MainLoop()
