#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
dshelper is a GUI for visualization of pandas dataframes.
In addition, it provides some functionalities in helping with some exploratory analysis and examination of raw data

Copyright (c) 2018 - 2021, Minchang (Carson) Zhang.
License: MIT (see LICENSE for details)
"""

from __future__ import absolute_import

from .dshelper import dshelp  # noqa
from . import data, plot  # noqa


__version__ = "0.1.0"

__all__ = ["dshelp"]
