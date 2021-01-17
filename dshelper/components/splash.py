import os
from pathlib import Path

import wx


def show_splash():
    # create, show and return the splash screen
    filename = os.path.join(
        Path(__file__).parent.parent.absolute(), "media", "splash.png"
    )
    bitmap = wx.Bitmap(filename, wx.BITMAP_TYPE_PNG)
    splash = wx.adv.SplashScreen(
        bitmap, wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_NO_TIMEOUT, 0, None, -1
    )
    splash.Show()
    return splash
