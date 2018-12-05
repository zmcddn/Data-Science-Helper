import wx

import pandas as pd
import numpy as np
from numpy import arange, sin, pi

from wx.lib.pubsub import pub

import matplotlib
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



class HeatPanel(wx.Panel):
    """
    A panel displays the histogram plot for any given column
    """

    def __init__(self, parent, df=None):
        wx.Panel.__init__(self, parent)

        self.df = df
        self.available_columns = list(self.df.columns)

        self.splitter = wx.SplitterWindow(self, wx.ID_ANY)
        self.heatmap_panel = wx.Panel(self.splitter, 1)
        self.correlation_panel = wx.Panel(self.splitter, 1)
        self.splitter.SplitVertically(self.heatmap_panel, self.correlation_panel)
        self.splitter.SetSashGravity(0.5)  # Set proportion for the splitter window
        self.splitter.Unsplit(self.correlation_panel)  # Hide when first load

        self.buttonpanel = wx.Panel(self, 1)  # Panel contains all the buttons
        self.buttonpanel.SetBackgroundColour("white")

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.heatmap_panel, -1, self.figure)
        self.color_bar = None  # Flag for color bar
        self.toolbar = NavigationToolbar(self.canvas)

        self.correlation_figure = Figure()
        self.correlation_axes = self.correlation_figure.add_subplot(111)
        self.correlation_canvas = FigureCanvas(
            self.correlation_panel, -1, self.correlation_figure
        )
        self.correlation_toolbar = NavigationToolbar(self.correlation_canvas)
        self.has_correlation_plot = False  # Flag for correlation plot

        # Drop-down select boxes
        self.text_y_axis = wx.StaticText(self.buttonpanel, label='Y Axis:')
        self.text_x_axis = wx.StaticText(self.buttonpanel, label='X Axis:')
        self.column1 = wx.ComboBox(
            self.buttonpanel, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.column2 = wx.ComboBox(
            self.buttonpanel, choices=self.available_columns, style=wx.CB_READONLY
        )
        self.Bind(wx.EVT_COMBOBOX, self.column_selected)

        # Create a button to display/hide correlation map
        self.correlation_button = wx.ToggleButton(
            self.buttonpanel, label="Display Correlation Map"
        )
        self.correlation_button.SetForegroundColour("blue")
        self.correlation_button.SetBackgroundColour("#D5F5E3")
        self.Bind(wx.EVT_TOGGLEBUTTON, self.correlation_heatmap)

        # Heatmap layout
        canvas_sizer = wx.BoxSizer(wx.VERTICAL)
        canvas_sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        canvas_sizer.Add(self.toolbar, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.heatmap_panel.SetSizer(canvas_sizer)

        # Correlation layout
        correlation_sizer = wx.BoxSizer(wx.VERTICAL)
        correlation_sizer.Add(self.correlation_canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        correlation_sizer.Add(self.correlation_toolbar, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.correlation_panel.SetSizer(correlation_sizer)

        # Bottom button bar layout
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.text_x_axis, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.column1, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.text_y_axis, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(self.column2, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        button_sizer.Add(
            self.correlation_button, 0, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER, 2
        )
        self.buttonpanel.SetSizer(button_sizer)

        # Main panel layout
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.splitter, 1, wx.EXPAND | wx.ALL)
        sizer.Add(self.buttonpanel)
        self.SetSizer(sizer)
        self.Fit()

        pub.subscribe(self.update_available_column, "UPDATE_DISPLAYED_COLUMNS")

    def column_selected(self, event):
        selected_column_id_1 = self.column1.GetCurrentSelection()
        selcted_column_1 = self.available_columns[selected_column_id_1]

        selected_column_id_2 = self.column2.GetCurrentSelection()
        selcted_column_2 = self.available_columns[selected_column_id_2]

        if selected_column_id_1 > 0 and selected_column_id_2 > 0:
            self.draw_heat(
                selcted_column_1,
                selcted_column_2,
                self.df[selcted_column_1],
                self.df[selcted_column_2],
            )

    def draw_heat(self, column1, column2, data1, data2):
        # Reset plot first
        self.axes.clear()

        if self.color_bar:
            self.color_bar.remove()

        # Check data type
        if data1.dtype == "object":
            new_df_1 = self.df.assign(id=(self.df[column1]).astype('category').cat.codes)
            data1 = new_df_1["id"]

            labels = list(pd.unique(new_df_1[column1].values))
            label_pos = list(pd.unique(new_df_1["id"].values))

            def format_fn(tick_val, tick_pos):
                if int(tick_val) in data1:
                    return labels[label_pos.index(int(tick_val))]
                else:
                    return ''
            self.axes.xaxis.set_major_formatter(FuncFormatter(format_fn))
            self.axes.xaxis.set_major_locator(MaxNLocator(integer=True))

        elif data2.dtype == "object":
            new_df_2 = self.df.assign(id=(self.df[column2]).astype('category').cat.codes)
            data2 = new_df_2["id"]

            labels = list(pd.unique(new_df_2[column2].values))
            label_pos = list(pd.unique(new_df_2["id"].values))

            def format_fn(tick_val, tick_pos):
                if int(tick_val) in data2:
                    return labels[label_pos.index(int(tick_val))]
                else:
                    return ''
            self.axes.yaxis.set_major_formatter(FuncFormatter(format_fn))
            self.axes.yaxis.set_major_locator(MaxNLocator(integer=True))

        heatmap = self.axes.hist2d(
            data1.fillna(0), data2.fillna(0), cmap=cm.tab20c, cmin=1
        )

        # # Adds cross marks for null values
        # self.axes.patch.set(hatch='xx', edgecolor='black')

        # To-do: plot using seaborn
        # colormap = sns.diverging_palette(220, 10, as_cmap=True)
        # df = self.df.pivot(column1, column2)
        # sns.heatmap(df, ax=self.axes, cmap=colormap)

        # Set plot info
        self.axes.set_title("Heat Map Plot for {} and {}".format(column1, column2))
        self.axes.set_ylabel(column2)
        self.axes.set_xlabel(column1)
        self.color_bar = self.figure.colorbar(heatmap[3], ax=self.axes)
        self.canvas.draw()

    def update_available_column(self, available_columns):
        self.available_columns = available_columns
        self.column1.Clear()
        self.column2.Clear()
        for column in self.available_columns:
            self.column1.Append(column)
            self.column2.Append(column)

    def correlation_heatmap(self, event):
        if self.correlation_button.GetValue() == True:
            # Show correlation plot
            self.splitter.SplitVertically(self.heatmap_panel, self.correlation_panel)
            self.correlation_button.SetLabel("Hide Correlation Map")
            self.correlation_button.SetForegroundColour("orange")

            if not self.has_correlation_plot:
                # Plot correlation heatmap
                self.correlation_axes.clear()
                df = self.df[self.available_columns]
                colormap = sns.diverging_palette(220, 10, as_cmap=True)

                _ = sns.heatmap(
                    df.corr(),
                    cmap=colormap,
                    square=True,
                    cbar_kws={"shrink": 0.9},
                    ax=self.correlation_axes,
                    annot=True,
                    linewidths=0.1,
                    vmax=1.0,
                    linecolor="white",
                    annot_kws={"fontsize": 12},
                )
                self.canvas.draw()
                self.has_correlation_plot = True

        if self.correlation_button.GetValue() == False:
            # Hide correlation plot
            self.splitter.Unsplit(self.correlation_panel)
            self.correlation_button.SetLabel("Display Correlation Map")
            self.correlation_button.SetForegroundColour("blue")
