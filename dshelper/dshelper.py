#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dshelper is a GUI for visualization of pandas dataframes. 
In addition, it provides some functionalities in helping with some exploratory analysis and examination of raw data

Copyright (c) 2018 - 2019, Minchang (Carson) Zhang.
License: MIT (see LICENSE for details)
"""

import wx
import wx.grid

import pandas as pd
import numpy as np
import datetime

from data.data_panel import DataTablePanel

EVEN_ROW_COLOUR = "#CCE6FF"
ODD_ROW_COLOUR = "#F0F8FF"
GRID_LINE_COLOUR = "#D3D3D3"


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


class DFSplitterPanel(wx.Panel):
    """
    A top and bottom splitter panel to display dataframe data and summary (i.e. df.describe)
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
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
        self.raw_data_page = DataTablePanel(data_notebook, -1)
        self.plot_page = wx.Panel(data_notebook)
        self.raw_data_page.SetBackgroundColour("WHITE")
        self.plot_page.SetBackgroundColour("YELLOW")

        # Add pages into the notebook for display
        data_notebook.AddPage(self.raw_data_page, "Raw Data")
        data_notebook.AddPage(self.plot_page, "Plot")

        # Put the notebook in a sizer in the panel for layout
        sizer = wx.BoxSizer()
        sizer.Add(data_notebook, 1, wx.EXPAND | wx.SP_NOBORDER)
        topPanel.SetSizer(sizer)

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

    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)
        splitter = wx.SplitterWindow(
            self, style=wx.SP_NOBORDER | wx.SP_3DSASH | wx.SP_LIVE_UPDATE
        )
        leftPanel = DFSplitterPanel(splitter)
        rightPanel = wx.Panel(splitter)
        leftPanel.SetBackgroundColour("YELLOW GREEN")
        rightPanel.SetBackgroundColour("SLATE BLUE")

        # Create a notebook for the right panel (log/stat panel)
        # each page serves a different function
        data_notebook = wx.Notebook(rightPanel)
        data_notebook.SetBackgroundColour("WHITE")
        self.info_page = wx.Panel(data_notebook)
        self.column_page = wx.Panel(data_notebook)
        self.log_page = LogPanel(data_notebook, -1)

        # Add pages into the notebook for display
        data_notebook.AddPage(self.info_page, "Info")
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


class MainFrame(wx.Frame):
    """Constructor"""

    def __init__(self, parent, id):
        wx.Frame.__init__(self, None, title="Data Science Helper")

        # self.sb=self.CreateStatusBar()

        self.main_splitter = SideSplitterPanel(self)

        # self.sb.SetStatusText("ss")

        self.Refresh()
        self.Show()
        self.Maximize(True)


if __name__ == "__main__":
    app = wx.App()
    MainFrame(None, -1)
    app.MainLoop()
