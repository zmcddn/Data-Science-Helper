from datetime import datetime

from pubsub import pub

import wx


class LogPanel(wx.Panel):
    """
    A panel displays the system logs.
    """

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, style=wx.BORDER_SUNKEN)

        style = wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL
        self.log = wx.TextCtrl(self, style=style)
        self.log.SetBackgroundColour("#D5F5E3")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.log, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        self.log.write(
            "Log begins here at time: {:%d, %b %Y, %H:%M}\n".format(
                datetime.now()
            )
        )
        self.log.write("wxPython version: {}\n".format(wx.__version__))

        pub.subscribe(self.PrintMessage, "LOG_MESSAGE")

    def PrintMessage(self, log_message):
        """
        The main function used to receive all the messages from different
        panels among the software, and display the messages in the log panel.

        Args:
            log_message --> string: the message needs to be displayed
        Returns: None
        Raises: None
        """

        self.log.write(log_message)
        self.log.write("\n")
