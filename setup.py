#! /usr/bin/env python
#
# Copyright (C) 2018-2021 Minchang (Carson) Zhang

DESCRIPTION = "dshelper: A GUI tool to display pandas dataframe and draw plots in a few clicks"
LONG_DESCRIPTION = """\
dshelper is a visualization tool designed to help data scientists better examine their data sets.
It utilizes `wxpython <https://www.wxpython.org/>`_ and is closely integrated with `pandas <https://pandas.pydata.org/>`_ data structures and `matplotlib <https://matplotlib.org/>`_ for plotting.
Here are some of the functionalities that dshelper offers:
- A view with raw data and its statistics
- Drag on the header to re-arrange columns
- Left click on the right panel to show/hide columns
- Plots in a few clicks: histogram, heatmap, correlation, scatter, box, violin, pair
- Bottom right buttons to hide panels and focus on data set
- Easy to use in command line, jupyter notebook and docker
"""

DISTNAME = 'dshelper'
MAINTAINER = 'Minchang (Carson) Zhang'
MAINTAINER_EMAIL = 'minchang@ualberta.ca'
URL = 'https://github.com/zmcddn/Data-Science-Helper'
LICENSE = 'MIT'
DOWNLOAD_URL = 'https://github.com/zmcddn/Data-Science-Helper'
VERSION = '0.2.0'
PYTHON_REQUIRES = ">=3.7"

INSTALL_REQUIRES = [
    'wxpython>=4.0',
    'matplotlib>=3.3.0',
    'numpy>=1.19.0',
    'pandas>=1.1.0',
    'scikit-learn>=0.23.0',
    'seaborn>=0.11.0',
]

EXTRAS_REQUIRE = {
    'all': [
        'statsmodels>=0.12.0',
        'Pypubsub>=4.0',
        'scipy>=1.5.0',
    ]
}


PACKAGES = [
    'dshelper',
    'dshelper.components',
    'dshelper.data',
    'dshelper.datasets',
    'dshelper.media',
    'dshelper.plots',
]

CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    "Programming Language :: Python",
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'License :: OSI Approved :: MIT License',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Scientific/Engineering :: Analytics',
    'Topic :: Multimedia :: Graphics',
    'Operating System :: OS Independent',
    'Framework :: Wxpython',
]


if __name__ == "__main__":

    from setuptools import setup

    import sys
    if sys.version_info[:2] < (3, 7):
        raise RuntimeError("dshelper requires python >= 3.7.")

    setup(
        name=DISTNAME,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        python_requires=PYTHON_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
        packages=PACKAGES,
        classifiers=CLASSIFIERS
    )
