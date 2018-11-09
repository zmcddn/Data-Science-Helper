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
from wx.lib.pubsub import pub

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
        self.df = df
        table = DataTable(self.df)
        self.grid.SetTable(table, takeOwnership=True)
        self.grid.SetGridLineColour(GRID_LINE_COLOUR)

        # Setup row/column size and alignment
        self.grid.AutoSize()
        self.grid.EnableDragGridSize(False)
        self.grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
        self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        # This works, but then the select cells doesn't work as expected
        # Need another way of re-arrange columns
        self.grid.EnableDragColMove()
        self.Bind(wx.grid.EVT_GRID_COL_MOVE, self.OnColMove)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.grid, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(self.sizer)

        pub.subscribe(self._update_data, "UPDATE_DF")

    def OnColMove(self, evt):
        # Draging column
        colId = evt.GetCol()
        colPos = self.grid.GetColPos(colId)
        wx.CallAfter(self.OnColMoved, colId, colPos)
        # allow the move to complete

    def OnColMoved(self, colId, oldPos):
        cols = list(self.df.columns)

        # once the move is done, GetColPos() returns the new position
        newPos = self.grid.GetColPos(colId)

        # Send log message
        log_message = "Column '{}' changed from position {} to {}".format(
            cols[colId], oldPos, newPos
        )
        # print(colId, "from", oldPos, "to", newPos)
        pub.sendMessage("LOG_MESSAGE", log_message=log_message)

        # Reset the draged column for re-ploting the df
        # otherwise selecting the datafrom will skip columns
        self.grid.SetColPos(colId, oldPos)

        # Get column position
        if newPos > oldPos:
            # Drag rightward
            cols.insert(newPos, cols[oldPos])
            cols.pop(oldPos)
        else:
            # Drag leftward
            cols.insert(newPos, cols[oldPos])
            cols.pop(oldPos + 1)

        # Reset the df with new column position
        df = self.df.reindex(columns=cols)

        # Update df for display
        self._update_data(df)

    def _update_data(self, df):
        # Update the dataframe for display
        self.df = df

        table = DataTable(self.df)
        self.grid.SetTable(table, takeOwnership=True)
        self.grid.Refresh()
        self.grid.AutoSize()


class DataDescribePanel(wx.Panel):
    """
    A panel specifically for displaying data frame descriptive statistics
    """

    def __init__(self, parent, id, df=None):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)
        self.grid = wx.grid.Grid(self)

        self.parent = parent

        # Set grid for displaying df.describe as table
        self.df = df.describe()
        table = DataTable(self.df)
        self.grid.SetTable(table, takeOwnership=True)
        self.grid.SetGridLineColour(GRID_LINE_COLOUR)

        # Setup row/column size and alignment
        self.grid.AutoSize()
        self.grid.EnableDragGridSize(False)
        self.grid.SetRowLabelSize(wx.grid.GRID_AUTOSIZE)
        self.grid.SetDefaultCellAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.grid, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(self.sizer)


class ColumnSelectionList(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    """
    A listCtrl object showing all the columns 
    """

    def __init__(self, parent, *args, **kw):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

    #     self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.left_click)
    #     # self.Bind(wx.EVT_LIST_BEGIN_DRAG, self.left_drag)

    # def left_click(self, event):
    #     item = event.GetItem()
    #     print("Item selected:", item.GetText())
    #     event.skip()

    # def left_drag(self, event):
    #     print("left mouse drag")
    #     pass


class ColumnSelectionPanel(wx.Panel):
    """A panel shows the data column info"""

    def __init__(self, parent, id, df=None):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)

        self.df = df
        self.original_df = df.copy()
        self.enabled_column = list(self.df.columns)

        rows = []
        non_null_count = self.df.notnull().sum()
        null_count = self.df.isnull().sum()
        non_null_percentage = non_null_count / self.df.shape[0]
        for num, column_types in enumerate(self.df.dtypes):
            rows.append(
                (
                    self.df.columns[num],
                    str(column_types),
                    str(non_null_count[num]),
                    str(null_count[num]),
                    "{:.2%}".format(non_null_percentage[num]),
                )
            )

        self.column_list = ColumnSelectionList(self)

        self.column_list.InsertColumn(0, "Name")
        self.column_list.InsertColumn(1, "Type")
        self.column_list.InsertColumn(2, "Non Null")
        self.column_list.InsertColumn(3, "Null")
        self.column_list.InsertColumn(4, "Non Null Percentage")

        idx = 0
        for row in rows:
            if int(wx.__version__[0]) < 4:
                # wxpython 3 compatibility
                index = self.column_list.InsertStringItem(idx, row[0])
                self.column_list.SetStringItem(index, 1, row[1])
                self.column_list.SetStringItem(index, 2, row[2])
                self.column_list.SetStringItem(index, 3, row[3])
                self.column_list.SetStringItem(index, 4, row[4])
            else:
                # wxpython 4 way
                index = self.column_list.InsertItem(idx, row[0])
                self.column_list.SetItem(index, 1, row[1])
                self.column_list.SetItem(index, 2, row[2])
                self.column_list.SetItem(index, 3, row[3])
                self.column_list.SetItem(index, 4, row[4])
            idx += 1

        # Set the background color of the table
        row_num = self.column_list.GetItemCount()
        for index in range(row_num):
            self.column_list.SetItemBackgroundColour(index, "#D5F5E3")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.column_list, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.left_click)

    def left_click(self, event):
        # Left click on the row to select or deselect a column
        item = event.GetItem()
        column_name = item.GetText()

        background_color = self.column_list.GetItemBackgroundColour(
            event.GetIndex()
        ).GetAsString(wx.C2S_HTML_SYNTAX)
        if background_color == "#D5F5E3":
            self.column_list.SetItemBackgroundColour(event.GetIndex(), "#FCF3CF")

            # Update dataframe
            self.enabled_column.remove(column_name)
            _updated_df = self.df[self.enabled_column]
            pub.sendMessage("UPDATE_DF", df=_updated_df)

            # log action
            _log_message = "Column disabled: {}".format(column_name)
            pub.sendMessage("LOG_MESSAGE", log_message=_log_message)
        else:
            self.column_list.SetItemBackgroundColour(event.GetIndex(), "#D5F5E3")

            # Update dataframe
            self.enabled_column.append(column_name)
            _updated_df = self.original_df[self.enabled_column]
            pub.sendMessage("UPDATE_DF", df=_updated_df)

            # log action
            _log_message = "Column enabled: {}".format(column_name)
            pub.sendMessage("LOG_MESSAGE", log_message=_log_message)

        self.column_list.Select(event.GetIndex(), on=0)  # De-select row


if __name__ == "__main__":
    print(int(wx.__version__[0]))
