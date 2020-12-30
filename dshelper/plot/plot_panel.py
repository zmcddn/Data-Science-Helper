import sys

import wx

import pandas as pd
import numpy as np
from numpy import arange, sin, pi

import matplotlib
if 'linux' not in sys.platform:
    matplotlib.use("WXAgg")

# import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

from .hist import HistPanel
from .heat import HeatPanel
from .box_violin import BoxViolinPanel
from .pair import PairPanel
from .scatter import ScatterPanel


class PlotPanel(wx.Panel):
    """
    The main panel contains several plots

    Args:
        df --> pandas dataframe: passed internally for plotting

    Returns: None
    """

    def __init__(self, parent, df=None):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        self.df = df

        # Create a notebook to display different kind of plot in different tabs
        plot_notebook = wx.Notebook(self)
        plot_notebook.SetBackgroundColour("WHITE")
        self.hist_page = HistPanel(plot_notebook, df=self.df)
        self.heat_page = HeatPanel(plot_notebook, df=self.df)
        # self.distribution_page = wx.Panel(plot_notebook)
        self.scatter_page = ScatterPanel(plot_notebook, df=self.df)
        self.box_violin_page = BoxViolinPanel(plot_notebook, df=self.df)
        self.pair_page = PairPanel(plot_notebook, df=self.df)

        # Add pages into the notebook for display
        plot_notebook.AddPage(self.hist_page, "Histogram")
        plot_notebook.AddPage(self.heat_page, "Heat Map")
        # plot_notebook.AddPage(self.distribution_page, "Distribution")
        plot_notebook.AddPage(self.scatter_page, "Scatter Plot")
        plot_notebook.AddPage(self.box_violin_page, "Box and Violin Plots")
        plot_notebook.AddPage(self.pair_page, "Pair Plots")

        # Put the notebook in a sizer in the panel for layout
        sizer = wx.BoxSizer()
        sizer.Add(plot_notebook, 1, wx.EXPAND | wx.SP_NOBORDER)
        self.SetSizer(sizer)


if __name__ == "__main__":
    # Test for individual panel layout
    app = wx.App(0)
    frame = wx.Frame(None, wx.ID_ANY)
    fa = CanvasPanel(frame)
    fa.draw2()
    frame.Show()
    app.MainLoop()
