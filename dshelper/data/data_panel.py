#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dshelper is a GUI for visualization of pandas dataframes. 
In addition, it provides some functionalities in helping with some exploratory 
analysis and examination of raw data

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

    Args:
        data --> pandas dataframe: the df to be shown
    Returns: None
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

    Args:
        df --> pandas dataframe: passed internally
    Returns: None
    """

    def __init__(self, parent, id, df=None):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)
        self.grid = wx.grid.Grid(self)

        self.parent = parent

        # Set grid for displaying dataframe as table
        self.df = df
        self.original_df = df.copy()
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
        """
        Function responds to dragging column header.
        """

        colId = evt.GetCol()
        colPos = self.grid.GetColPos(colId)
        wx.CallAfter(self.OnColMoved, colId, colPos)
        # allow the move to complete

    def OnColMoved(self, colId, oldPos):
        """
        Function calculates where the column is dragged and droped.

        Args:
            colId: the column id in wxpython
            oldPos: the original column index before dragged
        Returns: None
        """

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

        if newPos != oldPos:
            # Get column position
            if newPos > oldPos:
                # Drag rightward
                newPos += 1
                cols.insert(newPos, cols[oldPos])
                cols.pop(oldPos)
            else:
                # Drag leftward
                cols.insert(newPos, cols[oldPos])
                cols.pop(oldPos + 1)

            # Reset the df with new column position
            df = self.df.reindex(columns=cols)

            pub.sendMessage(
                "UPDATE_COLUMNS",
                columns=df.shape[1],
                old_position=oldPos,
                new_position=newPos,
            )

            # Update df for display
            self._update_data(df)

    def _update_data(self, df):
        """
        Updates the displayed dataframe with new locations of columns.

        Args:
            df --> pandas dataframe: df with differnt column order to be displayed
        Returns: None
        """

        self.df = df

        table = DataTable(self.df)
        self.grid.SetTable(table, takeOwnership=True)
        self.grid.Refresh()
        self.grid.AutoSize()

        # Disable column re-ordering if some columns are hidden
        if self.df.shape[1] < self.original_df.shape[1]:
            self.grid.EnableDragColMove(False)
        else:
            self.grid.EnableDragColMove()


class DataDescribePanel(wx.Panel):
    """
    A panel for displaying data frame descriptive statistics (i.e. df.describe())

    Args:
        df --> pandas dataframe: pandas dataframe
    Returns: None
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
    A listCtrl object to enable auto-with for all columns.
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
    """
    A panel shows the data column info

    Args:
        df --> pandas dataframe: pandas dataframe
    Returns: None
    """

    def __init__(self, parent, id, df=None):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)

        self.df = df
        self.original_df = df.copy()
        self.enabled_columns = list(self.df.columns)
        self.original_columns = list(self.df.columns)

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

        self.rows = rows

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

        pub.subscribe(self._update_column, "UPDATE_COLUMNS")

    def left_click(self, event):
        """
        Responds to button left click on the row to select or deselect a column
        """

        item = event.GetItem()
        column_name = item.GetText()

        background_color = self.column_list.GetItemBackgroundColour(
            event.GetIndex()
        ).GetAsString(wx.C2S_HTML_SYNTAX)
        if background_color == "#D5F5E3":
            self.column_list.SetItemBackgroundColour(event.GetIndex(), "#FCF3CF")

            # Update dataframe
            self.enabled_columns.remove(column_name)
            _updated_df = self.df[self.enabled_columns]
            pub.sendMessage("UPDATE_DF", df=_updated_df)

            # log action
            _log_message = "\nColumn disabled: {}".format(column_name)
            pub.sendMessage("LOG_MESSAGE", log_message=_log_message)

            # Update displayed columns
            pub.sendMessage(
                "UPDATE_DISPLAYED_COLUMNS", available_columns=self.enabled_columns
            )
        else:
            self.column_list.SetItemBackgroundColour(event.GetIndex(), "#D5F5E3")

            # Update dataframe
            # column_index = self.original_columns.index(column_name)
            column_index, index_found = self.get_insert_index(column_name)
            if index_found:
                self.enabled_columns.insert(column_index, column_name)
            else:
                self.enabled_columns.append(column_name)
            _updated_df = self.original_df[self.enabled_columns]
            pub.sendMessage("UPDATE_DF", df=_updated_df)

            # log action
            _log_message = "\nColumn enabled: {}".format(column_name)
            pub.sendMessage("LOG_MESSAGE", log_message=_log_message)

            # Update displayed columns
            pub.sendMessage(
                "UPDATE_DISPLAYED_COLUMNS", available_columns=self.enabled_columns
            )

        self.column_list.Select(event.GetIndex(), on=0)  # De-select row

    def get_insert_index(self, column_name):
        """
        Function to get the inset index for any given column name

        Args:
            column_name --> string: the column name in df
        Returns: 
            column_index --> int: the index where the column is inserted
            index_found --> bool: a flag shows whether the index is found
        """

        _column_index = self.original_columns.index(column_name)
        index_found = False
        if _column_index == 0:
            # case for the beginning position
            column_index = _column_index
            index_found = True
        elif _column_index == len(self.original_columns) - 1:
            # case for the ending position
            column_index = _column_index
            index_found = True
        else:
            # Always search from the leftward
            while _column_index > 0:
                _column_index -= 1
                previous_column = self.original_columns[_column_index]
                # print("c-column:",column_name, "index:", _column_index, "p-column:", previous_column)
                if previous_column in self.enabled_columns:
                    column_index = self.enabled_columns.index(previous_column) + 1
                    index_found = True
                    # print("inser index:", column_index)
                    break

            if not index_found:
                # case when all the left columns are hidden
                column_index = 0
                index_found = True

        return column_index, index_found

    def _update_column(self, columns, old_position, new_position):
        """
        An internal helper function to update the column positions for 
        drag-and-drop action.

        Args:
            columns --> list: pandas df column header list
            old_position --> int: original column position before dragging
            new_position --> int: new column position after dropping
        Returns: None
        """
        
        if columns == self.original_df.shape[1]:
            # case for re-arrangement without hidden columns

            # Add to new position
            if old_position != new_position:
                # Delete from old position
                self.column_list.DeleteItem(old_position)

                if old_position < new_position:
                    idx = new_position - 1
                elif old_position > new_position:
                    idx = new_position
                if int(wx.__version__[0]) < 4:
                    # wxpython 3 compatibility
                    index = self.column_list.InsertStringItem(
                        idx, self.rows[old_position][0]
                    )
                    self.column_list.SetStringItem(index, 1, self.rows[old_position][1])
                    self.column_list.SetStringItem(index, 2, self.rows[old_position][2])
                    self.column_list.SetStringItem(index, 3, self.rows[old_position][3])
                    self.column_list.SetStringItem(index, 4, self.rows[old_position][4])
                else:
                    # wxpython 4 way
                    index = self.column_list.InsertItem(idx, self.rows[old_position][0])
                    self.column_list.SetItem(index, 1, self.rows[old_position][1])
                    self.column_list.SetItem(index, 2, self.rows[old_position][2])
                    self.column_list.SetItem(index, 3, self.rows[old_position][3])
                    self.column_list.SetItem(index, 4, self.rows[old_position][4])

                # Set inserted row background color
                self.column_list.SetItemBackgroundColour(index, "#D5F5E3")

                # Update rows
                moved_row = self.rows.pop(old_position)
                self.rows.insert(idx, moved_row)

                # Update df columns info
                moved_column = self.enabled_columns.pop(old_position)
                self.enabled_columns.insert(idx, moved_column)

                # Update original columns info
                moved_column = self.original_columns.pop(old_position)
                self.original_columns.insert(idx, moved_column)

                # Update df
                self.df = self.df[self.enabled_columns]
        else:
            # case for re-arrangement with hidden columns

            # # Set the background color of the table
            # row_num = self.column_list.GetItemCount()
            # for index in range(row_num):
            #     self.column_list.SetItemBackgroundColour(index, "#D5F5E3")

            pass


if __name__ == "__main__":
    print(int(wx.__version__[0]))
