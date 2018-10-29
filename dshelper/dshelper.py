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

EVEN_ROW_COLOUR = "#CCE6FF"
ODD_ROW_COLOUR = "#F0F8FF"
GRID_LINE_COLOUR = "#D3D3D3"


class DataTable(wx.grid.PyGridTableBase):
    """
    A grid table to show dataframe 
    """

    def __init__(self, data=None):
        wx.grid.PyGridTableBase.__init__(self)

        self.INIT_ROWS = 40
        self.INIT_COLS = 100

        if data is None:
            # Initiate UI
            self.data = pd.DataFrame(
                index=list(range(1, self.INIT_ROWS)),
                columns=list(range(1, self.INIT_COLS)),
            ).fillna("")
        else:
            self.data = data

        self.odd = wx.grid.GridCellAttr()
        self.odd.SetBackgroundColour(ODD_ROW_COLOUR)
        self.odd.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.even = wx.grid.GridCellAttr()
        self.even.SetBackgroundColour(EVEN_ROW_COLOUR)
        self.even.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))

    def GetNumberRows(self):
        return self.data.shape[0]

    def GetNumberCols(self):
        return self.data.shape[1]

    def GetValue(self, row, col):
        # if col == 0:
        # # Display index as a column
        #     return self.data.index[row]
        return self.data.iloc[row, col]

    def SetValue(self, row, col, value):
        # self.data.iloc[row, col-1] = value
        pass

    def GetColLabelValue(self, col):
        # if col == 0:
        # # Display index as a column
        #     if self.data.index.name is None:
        #         return 'Index'
        #     else:
        #         return self.data.index.name
        return self.data.columns[col]

    def GetRowLabelValue(self, row):
        return str(self.data.index[row])

    def GetTypeName(self, row, col):
        return wx.grid.GRID_VALUE_STRING

    def GetAttr(self, row, col, prop):
        attr = [self.even, self.odd][row % 2]
        attr.IncRef()
        return attr

    """
    The following refresh method is copied fom the following link:
    https://bitbucket.org/driscollis/mousevspython/src/3f5ff00ce6f3/wxpython_by_example/grids/gridTableBaseEx.py?fileviewer=file-view-default
    """

    def ResetView(self):
        """Trim/extend the control's rows and update all values"""
        self.getGrid().BeginBatch()
        for current, new, delmsg, addmsg in [
            (
                self.currentRows,
                self.GetNumberRows(),
                wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED,
                wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED,
            ),
            (
                self.currentColumns,
                self.GetNumberCols(),
                wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED,
                wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED,
            ),
        ]:
            if new < current:
                msg = wx.grid.GridTableMessage(
                    self, delmsg, new, current - new  # position
                )
                self.getGrid().ProcessTableMessage(msg)
            elif new > current:
                msg = wx.grid.GridTableMessage(self, addmsg, new - current)
                self.getGrid().ProcessTableMessage(msg)
        self.UpdateValues()
        self.getGrid().EndBatch()

        # The scroll bars aren't resized (at least on windows)
        # Jiggling the size of the window rescales the scrollbars
        h, w = grid.GetSize()
        grid.SetSize((h + 1, w))
        grid.SetSize((h, w))
        grid.ForceRefresh()

    def UpdateValues(self):
        """Update all displayed values"""
        msg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.getGrid().ProcessTableMessage(msg)


class DataTablePanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)
        self.grid = wx.grid.Grid(self)

        self.parent = parent

        # Test dataframe
        todays_date = datetime.datetime.now().date()
        index = pd.date_range(
            todays_date - datetime.timedelta(10), periods=10, freq="D"
        )
        df = pd.DataFrame(index=index, columns=list(range(30)))
        df = df.fillna(500)
        # df.reset_index(inplace=True)
        # df = pd.DataFrame(np.random.random((10, 5)))
        # print(df)

        # Set grid for displaying dataframe as table
        table = DataTable(df)
        self.grid.SetTable(table)
        self.grid.SetGridLineColour(GRID_LINE_COLOUR)

        # Setup row/column size and alignment
        self.grid.AutoSize()
        self.grid.EnableDragGridSize(False)
        self.grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
        self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        # pub.subscribe(self.getResult, "analysisOrderCondition")


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
