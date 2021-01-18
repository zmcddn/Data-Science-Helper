import sys

import wx

from pubsub import pub

import matplotlib
if "linux" not in sys.platform:
    matplotlib.use("WXAgg")

try:
    import seaborn as sns
    sns.set()
except ImportError:
    pass

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx as NavigationToolbar
from matplotlib.figure import Figure

try:
    # local import
    from components import create_bitmap_dropdown_menu
except (ModuleNotFoundError, ImportError):
    # Package import
    from dshelper.components import create_bitmap_dropdown_menu

from .utils import make_pair_plot


class PairPanel(wx.Panel):
    """
    A panel displays the pair plots for any given column

    Args:
        df --> pandas dataframe: passed internally for plotting

    Returns: None
    """

    def __init__(self, parent, df=None):
        wx.Panel.__init__(self, parent)

        self.df = df

        self.available_columns = list(self.df.columns)
        self.hue_columns = self._get_hue_column()

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)

        self.toolbar = NavigationToolbar(self.canvas)

        self.text_hue = wx.StaticText(self, label="Hue:")
        self.dropdown_menu = create_bitmap_dropdown_menu(
            self, self.hue_columns, self.df
        )
        self.Bind(wx.EVT_COMBOBOX, self.column_selected)

        toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        toolbar_sizer.Add(self.text_hue, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        toolbar_sizer.Add(self.dropdown_menu, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        toolbar_sizer.Add(self.toolbar, 0, wx.ALL, 5)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        sizer.Add(toolbar_sizer)
        self.SetSizer(sizer)
        self.Fit()

        pub.subscribe(self.update_available_column, "UPDATE_DISPLAYED_COLUMNS")

    def column_selected(self, event):
        """
        Function responses to select column from dropdown menu.
        """

        selected_column = self.dropdown_menu.GetStringSelection()

        self.draw_pair(selected_column)

    def draw_pair(self, column_name):
        """
        Function that draws plot in the panel.

        Note:
            Seaborn pairplot return a series of subplots within one figure,
            therefore it is really difficult to plot it directly in the
            existing figure.
            Instead, we mimic how it is plotted and add corresponding
            number of matplotlib subplots and plot the pairplot inside the
            matplotlib subplots

        Args:
            column_name --> string: the name of the column that needs to
                be drawn
        Returns: None
        """

        make_pair_plot(self.figure, self.df, column_name, self.available_columns)

        self.canvas.draw()
        self.Refresh()

    def _get_hue_column(self):
        """
        This internal function limits the available columns for hue selection.
        It filters out those columns with too many dinstinct values.

        Currently it is set for the number 6, which is the number of distinct
        colors for the default seaborn color palette.

        Args: None

        Returns:
            hue_columns --> list: a list of column headers
        """

        hue_columns = []
        for column in self.available_columns:
            if self.df[column].nunique() <= 6:
                # Restrict hue selection based on distinct values in column
                hue_columns.append(column)

        return hue_columns

    def update_available_column(self, available_columns):
        """
        Update dataframe used for plotting.

        Args:
            available_columns --> list: a list of available column headers

        Returns: None
        """

        self.available_columns = available_columns

        # Update hue column selection
        self.hue_columns = self._get_hue_column()

        # Update dropdown menu
        self.dropdown_menu.Clear()
        for column in self.hue_columns:
            self.dropdown_menu.Append(column)
