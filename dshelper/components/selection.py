import os

import wx
from wx.adv import BitmapComboBox


def create_bitmap_dropdown_menu(panel, available_columns, df):
    dropdown_menu = BitmapComboBox(panel, style=wx.CB_READONLY)
    for column in available_columns:
        n_distinct = df[column].nunique()

        if n_distinct <= 9:
            filename = os.path.join(os.getcwd(), "media", f"{n_distinct}.png")
        else:
            filename = os.path.join(os.getcwd(), "media", "forest.png")

        if os.path.exists(filename):
            image = wx.Image(filename)
            image.Rescale(16, 16, quality=wx.IMAGE_QUALITY_HIGH)
            icon = wx.Bitmap(image)
            dropdown_menu.Append(column, bitmap=icon)
        else:
            dropdown_menu.Append(column)

    return dropdown_menu
