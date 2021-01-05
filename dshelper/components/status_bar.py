import wx

from pubsub import pub


class MyStatusBar(wx.StatusBar):
    """
    Custom status bar for positioning extra functioning buttons inside the
    status bar.

    Args: None
    Returns: None
    """

    def __init__(self, parent, memory_usage):
        wx.StatusBar.__init__(self, parent)

        self.SetFieldsCount(5)
        self.SetStatusWidths([80, 120, -1, 200, 200])
        self.sizeChanged = False
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        # Text fields with initial content
        self.SetStatusText("some text", 0)
        self.SetStatusText("some text", 1)
        self.memory = wx.StaticText(self, -1, f" Memory Usage: {memory_usage}")
        self.memory.SetForegroundColour("blue")

        # Field for buttons
        self.hide_show_bottom = wx.ToggleButton(self, -1, "Hide Bottom Panel")
        self.hide_show_side = wx.ToggleButton(self, -1, "Hide Right Panel")

        # Set button styles for attention
        self.hide_show_bottom.SetForegroundColour("orange")
        self.hide_show_bottom.SetBackgroundColour("#FDE68B")  # light yellow
        self.hide_show_side.SetForegroundColour("orange")
        self.hide_show_side.SetBackgroundColour("#FDE68B")  # light yellow

        # Button functions
        self.Bind(wx.EVT_TOGGLEBUTTON, self.hide_show_panels)

        # set the initial position for buttons
        self.Reposition()

    def OnSize(self, evt):
        evt.Skip()
        self.Reposition()  # for normal size events

        # Set a flag so the idle time handler will also do the repositioning.
        # It is done this way to get around a buglet where GetFieldRect is not
        # accurate during the EVT_SIZE resulting from a frame maximize.
        self.sizeChanged = True

    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()

    def Reposition(self):
        """Reposition for widgets inside status bar"""

        # Static text (memory usage)
        rect0 = self.GetFieldRect(2)
        rect0.x += 1
        rect0.y += 1
        self.memory.SetRect(rect0)

        # Button (hide show bottom panel)
        rect1 = self.GetFieldRect(3)
        rect1.x += 1
        rect1.y += 1
        self.hide_show_bottom.SetRect(rect1)

        # Button (hide show side panel)
        rect2 = self.GetFieldRect(4)
        rect2.x += 1
        rect2.y += 1
        self.hide_show_side.SetRect(rect2)

        self.sizeChanged = False

    def hide_show_panels(self, event):
        """
        One button function that responds to two buttons clicking event.
        Each button's clicking event is captured and turn to its own function.
        """

        # Function for bottom panel
        if self.hide_show_bottom.GetValue() == True:
            # Hide bottom panel
            pub.sendMessage("BOTTOM_PANEL", status="hide")
            self.hide_show_bottom.SetLabel("Show Bottom Panel")
            self.hide_show_bottom.SetForegroundColour("blue")
            self.hide_show_bottom.SetBackgroundColour("#C8FD8B")  # light green
        elif self.hide_show_bottom.GetValue() == False:
            # Show bottom panel
            pub.sendMessage("BOTTOM_PANEL", status="show")
            self.hide_show_bottom.SetLabel("Hide Bottom Panel")
            self.hide_show_bottom.SetForegroundColour("orange")
            self.hide_show_bottom.SetBackgroundColour("#FDE68B")  # light yellow

        # Function for right panel
        if self.hide_show_side.GetValue() == True:
            # Hide bottom panel
            pub.sendMessage("RIGHT_PANEL", status="hide")
            self.hide_show_side.SetLabel("Show Right Panel")
            self.hide_show_side.SetForegroundColour("blue")
            self.hide_show_side.SetBackgroundColour("#C8FD8B")  # light green
        elif self.hide_show_side.GetValue() == False:
            # Show bottom panel
            pub.sendMessage("RIGHT_PANEL", status="show")
            self.hide_show_side.SetLabel("Hide Right Panel")
            self.hide_show_side.SetForegroundColour("orange")
            self.hide_show_side.SetBackgroundColour("#FDE68B")  # light yellow
