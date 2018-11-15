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


class HistPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

    def draw(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)
        self.axes.plot(t, s)

    def draw2(self):
        t = arange(0.0, 5.0, 0.01)
        s = sin(2 * t)
        self.axes.hist2d(t, s)


if __name__ == "__main__":
    # Test for indivial panel layout
    app = wx.App(0)
    frame = wx.Frame(None, wx.ID_ANY)
    fa = CanvasPanel(frame)
    fa.draw2()
    frame.Show()
    app.MainLoop()
