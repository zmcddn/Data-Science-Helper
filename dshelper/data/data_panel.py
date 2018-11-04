#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dshelper is a GUI for visualization of pandas dataframes. 
In addition, it provides some functionalities in helping with some exploratory analysis and examination of raw data

Copyright (c) 2018 - 2019, Minchang (Carson) Zhang.
License: MIT (see LICENSE for details)
"""

import datetime
import io

import pandas as pd
import numpy as np

import wx
import wx.grid
import wx.lib.mixins.listctrl

if int(wx.__version__[0]) < 4:
    # Add compatibility with wxpython 3.*
    GRID_TABLE_CONSTRUCTOR = wx.grid.PyGridTableBase
else:
    GRID_TABLE_CONSTRUCTOR = wx.grid.GridTableBase

EVEN_ROW_COLOUR = "#CCE6FF"
ODD_ROW_COLOUR = "#F0F8FF"
GRID_LINE_COLOUR = "#D3D3D3"


class DataTable(GRID_TABLE_CONSTRUCTOR):
    """
    A grid table to show dataframe 
    """

    def __init__(self, data=None):
        GRID_TABLE_CONSTRUCTOR.__init__(self)

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
        return str(self.data.columns[col])

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
    """
    A panel displays the data in tabular format
    """

    def __init__(self, parent, id, df=None):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)
        self.grid = wx.grid.Grid(self)

        self.parent = parent

        # Set grid for displaying dataframe as table
        table = DataTable(df)
        self.grid.SetTable(table, takeOwnership=True)
        self.grid.SetGridLineColour(GRID_LINE_COLOUR)

        # Setup row/column size and alignment
        self.grid.AutoSize()
        self.grid.EnableDragGridSize(False)
        self.grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
        self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # This works, but then the select cells doesn't work as expected
        # Need another way of re-arrange columns
        # self.grid.EnableDragColMove()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.grid, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        # pub.subscribe(self.getResult, "analysisOrderCondition")


class InfoPanel(wx.Panel):
    """A panel shows the data info"""

    def __init__(self, parent, id, df=None):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)

        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        font1 = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u"Consolas")
        self.df_info = wx.TextCtrl(self, style=style)
        self.df_info.SetFont(font1)
        self.df_info.SetBackgroundColour("#FCF3CF")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.df_info, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        if df is None:
            self.df_info.write("Please import a dataframe")
        else:
            buffer = io.StringIO()
            df.info(buf=buffer)
            s = buffer.getvalue()
            self.df_info.write(s)


class ColumnSelectionList(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    """
    A listCtrl object showing all the columns 
    """

    def __init__(self, parent, *args, **kw):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)


class ColumnSelectionPanel(wx.Panel):
    """A panel shows the data column info"""

    def __init__(self, parent, id, df=None):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)

        self.df = df

        rows = []
        for num, column_types in enumerate(self.df.dtypes):
            rows.append((self.df.columns[num], str(column_types)))

        self.column_list = ColumnSelectionList(self)

        self.column_list.InsertColumn(0, "Name")
        self.column_list.InsertColumn(1, "Type")

        idx = 0
        for row in rows:
            if int(wx.__version__[0]) < 4:
                # wxpython 3 compatibility
                index = self.column_list.InsertStringItem(idx, row[0])
                self.column_list.SetStringItem(index, 1, row[1])
            else:
                # wxpython 4 way
                index = self.column_list.InsertItem(idx, row[0])
                self.column_list.SetItem(index, 1, row[1])
            idx += 1

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.column_list, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)


if __name__ == "__main__":
    print(int(wx.__version__[0]))
