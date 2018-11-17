import wx

import pandas as pd
import numpy as np
from numpy import arange, sin, pi

import matplotlib

# import seaborn as sns

matplotlib.use("WXAgg")

# import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

from .hist import HistPanel
from .heat import HeatPanel


class PlotPanel(wx.Panel):
    """
    A panel contains several plots
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
        self.distribution_page = wx.Panel(plot_notebook)
        self.scatter_page = wx.Panel(plot_notebook)
        self.boxplot_page = wx.Panel(plot_notebook)
        self.violin_page = wx.Panel(plot_notebook)

        # Add pages into the notebook for display
        plot_notebook.AddPage(self.hist_page, "Histogram")
        plot_notebook.AddPage(self.heat_page, "Heat Map")
        plot_notebook.AddPage(self.distribution_page, "Distribution")
        plot_notebook.AddPage(self.scatter_page, "Scatter Plot")
        plot_notebook.AddPage(self.boxplot_page, "Box Plot")
        plot_notebook.AddPage(self.violin_page, "Violin Plot")

        # Put the notebook in a sizer in the panel for layout
        sizer = wx.BoxSizer()
        sizer.Add(plot_notebook, 1, wx.EXPAND | wx.SP_NOBORDER)
        self.SetSizer(sizer)


if __name__ == "__main__":
    # Test for indivial panel layout
    app = wx.App(0)
    frame = wx.Frame(None, wx.ID_ANY)
    fa = CanvasPanel(frame)
    fa.draw2()
    frame.Show()
    app.MainLoop()
