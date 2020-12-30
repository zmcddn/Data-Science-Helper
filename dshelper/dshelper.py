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
import os

import pandas as pd
import numpy as np

import wx
import wx.grid
from pubsub import pub

# Local package imports
try:
    from .data import data_panel as data
    from .plot import plot_panel as plot
    from .datasets import fetch_titanic
except (ModuleNotFoundError, ImportError):
    import data, plot
    from datasets import fetch_titanic

# Python 2 compatibility
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

EVEN_ROW_COLOUR = "#CCE6FF"
ODD_ROW_COLOUR = "#F0F8FF"
GRID_LINE_COLOUR = "#D3D3D3"


def get_df():
    # Initial dataframe
    df = pd.DataFrame(
        np.nan, index=list(range(30)), columns=['A','B','C','D','E','F','G']
    )

    # df = fetch_titanic(with_random_date=True)

    return df


class LogPanel(wx.Panel):
    """
    A panel displays the system logs.
    """

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
        """
        The main funciton used to receive all the messages from different
        panels among the software, and display the messages in the log panel.

        Args:
            log_message --> string: the message needs to be displayed
        Returns: None
        Raises: None
        """

        self.log.write(log_message)
        self.log.write("\n")


class DFSplitterPanel(wx.Panel):
    """
    A top and bottom splitter panel to display dataframe data in the
    top panel and summary of the data (i.e. df.describe) in the bottom
    panel.

    Args:
        df --> pandas dataframe: df passed internally for inspection
    Return: None
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
        self.raw_data_page = data.DataTablePanel(data_notebook, -1, df=self.df)
        self.plot_page = plot.PlotPanel(data_notebook, df=self.df)
        self.raw_data_page.SetBackgroundColour("WHITE")
        self.plot_page.SetBackgroundColour("YELLOW")

        # Add pages into the notebook for display
        data_notebook.AddPage(self.raw_data_page, "Raw Data")
        data_notebook.AddPage(self.plot_page, "Plots")

        # Put the notebook in a sizer in the panel for layout
        sizer = wx.BoxSizer()
        sizer.Add(data_notebook, 1, wx.EXPAND | wx.SP_NOBORDER)
        self.topPanel.SetSizer(sizer)

        self.data_describe = data.DataDescribePanel(
            self.bottomPanel, -1, df=self.df
        )
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
        """
        A button function to show/hide bottom panel (i.e. dataframe summary)

        Args:
            status --> string: the flag sent by clicking the button
        Returns: None
        """

        if status == "hide":
            self.splitter.Unsplit(self.bottomPanel)

        if status == "show":
            self.splitter.SplitHorizontally(self.topPanel, self.bottomPanel)


class SideSplitterPanel(wx.Panel):
    """
    A left and right splitter panel to display the dataframe in the left panel
    and log/stats in the right panel.

    Args:
        df --> pandas dataframe: df passed internally for inspection
    Return: None
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
        self.column_page = data.ColumnSelectionPanel(
            data_notebook, -1, df=self.df
        )
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
        """
        A button function to show/hide right panel (i.e. column stats/logs)

        Args:
            status --> string: the flag sent by clicking the button
        Returns: None
        """

        if status == "hide":
            self.splitter.Unsplit(self.rightPanel)

        if status == "show":
            self.splitter.SplitVertically(self.leftPanel, self.rightPanel)


class MyStatusBar(wx.StatusBar):
    """
    Custom status bar for positioning extra functioning bnuttons inside the
    status bar.

    Args: None
    Returns: None
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
        """
        One button function that responds to two buttons clicking event.
        Each button's clicking event is captured and turn to its own function.
        """

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

    Args:
        df --> pandas dataframe: the df that you would like to inspect
    Return: None
    """

    def __init__(self, df, app=None):
        wx.Frame.__init__(self, None, -1, title="Data Science Helper")

        self.app = app

        if df is not None:
            self.df = prepare_df(df)
        else:
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
        """
        Function to update the datafram column statistics in the status bar.

        Args:
            df --> pandas dataframe: pass internally to examine the number of cols
        Returns: None
        """

        cols = df.shape[1]
        self.status_bar.SetStatusText(" Columns: {}".format(cols), 1)

    def OnCloseWindow(self, event):
        """
        Event function respond to the close of the main GUI window.
        """

        self.Destroy()
        # event.Skip()

        # # make sure that all is closed
        # for item in wx.GetTopLevelWindows():
        #     print(item, isinstance(item, MainFrame))
        #     if isinstance(item, MainFrame):
        #         item.Destroy()
            # if not isinstance(item, MainFrame):
            #     if isinstance(item, wx.Dialog):
            #         item.Destroy()
            #     item.Close()

        if "win32" in sys.platform:
            # Fix system related error:
            # forrtl: error (200): program aborting due to control-C event
            try:
                import win32api
                def doSaneThing(sig, func=None):
                    return True
                win32api.SetConsoleCtrlHandler(doSaneThing, 1)
            except ModuleNotFoundError:
                pass
        # # event.Skip()
        self.app.ExitMainLoop()


def prepare_df(df):
    """
    This function converts the df header into string format
    for the gui to be able to plot

    Args:
        df --> pandas dataframe: df needs to be cleaned
    Return:
        df --> pandas dataframe: cleaned df
    """

    columns = list(df.columns.values)
    for num, item in enumerate(columns):
        if not isinstance(item, str):
            columns[num] = "{}".format(item)

    df.columns = columns

    return df


def dshelp(df):
    """
    The function to run dshelper

    Args:
        df --> pandas dataframe: the df that you would like to inspect
    Returns: None
    """

    app = wx.App()
    frame = MainFrame(df, app)
    app.MainLoop()


if __name__ == "__main__":
    import dshelper
    dshelper.dshelp(None)
