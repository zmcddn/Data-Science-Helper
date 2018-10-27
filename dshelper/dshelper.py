#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dshelper is a GUI for visualization of pandas dataframes. 
In addition, it provides some functionalities in helping with some exploratory analysis and examination of raw data

Copyright (c) 2018 - 2019, Minchang (Carson) Zhang.
License: MIT (see LICENSE for details)
"""

import wx


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
        topPanel.SetBackgroundColour("SEA GREEN")
        bottomPanel.SetBackgroundColour("STEEL BLUE")

        # Create a notebook for the top panel (data panel)
        # each page serves a different function
        data_notebook = wx.Notebook(topPanel)
        self.raw_data_page = wx.Panel(data_notebook, -1)
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
        self.log_page = wx.Panel(data_notebook)

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
