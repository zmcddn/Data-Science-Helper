# Data Science Helper

A visualization tool designed to help data scientists better examine their data sets.

## Installation (its on PYPI !!)
```python
pip install dshelper
```

## Usage
```python
import dshelper
dshelper.dshelp(df)
```

## Feature

- ✅ Default view with raw data and its statistics info
- ✅ Drag on the header to re-arrange columns
- ✅ Left click on the right panel to show/hide columns
- ✅ Plots: histogram, heatmap, correlation, scatter, box, violin, pair 
- ✅ Bottom right buttons to hide panels and focus on data set
- ✅ Easy to see memory usage and logs in bottom status bar
- ✅ Easy to use in command line, jupyter notebook and docker

## Plots

- ✅ Histogram
- ✅ Heatmap
- ✅ Correlation 
- ✅ Scatter Plot
- ✅ Box Plot
- ✅ Violin Plot
- ✅ Pair plot

## Demo with Titanic data

The default view, main panel displays the dataset.
The bottom panel displays the statistics of the dataset
The right panel has two tabs, the first one displays the stats for all the columns, the second one displays the system logs.

![Main View](./screenshots/1.PNG)

The bottom and right panels can be hidden by clicking the buttons located on the bottom right of the window. This will allow data scientists to focus on the dataset and plots

![Focus View](./screenshots/2.PNG)

You can also drag and drop to re-arrange the column orders, click on the right column tab to hide columns in the main view.

![Hide View](./screenshots/9.PNG)

And below are a few plots:

![Histogram](./screenshots/3.PNG)
![Heatmap](./screenshots/4.PNG)
![Heatmap with Correlation plot](./screenshots/5.PNG)
![Scatter](./screenshots/6.PNG)
![Box and violin plots](./screenshots/7.PNG)
![Pair plots](./screenshots/8.PNG)

## Dependencies

* wxpython
* matplotlib
* seaborn
* pandas
* numpy
* scikit-learn
* scipy
* statsmodels

## How to run locally

* `git clone git@github.com:zmcddn/Data-Science-Helper.git`
* `conda create -n py36 python=3.6` or use virtualenv or pipenv
* `activate py36` (windows) or `source activate py36` (mac, linux)
* `conda install --yes --file requirements.txt` or `pip install -r requirements.txt`
* In case the `PyPubSub` is not installed with conda, you can do `pip install PyPubSub`
* `cd dshelper`
* `python main_gui.py` (windows, linux) or `pythonw main_gui.py` (mac)

For help with any dataframe, you can follow the following steps:
* `import dshelper`
* `dshelper.dshelp(df)`


## How to use in Jupyter Notebook

- For running in Jupyter Notebook you need to add `%gui wx` at the top of the file for the GUI to display properly

## Run with docker

* `make build` to build the project
* `make runlinux` to run in Linux
* WIP for mac

## To-do

- next version
    * [ ] Sort by columns
    * [ ] Import file (csv, excl)
    * [ ] Add menu
    * [ ] export file
    * [ ] ability to change cells
    * [ ] standalone version
- next big version
    * [ ] correlation analysis
    * [ ] feature importance
    * [ ] support large file (sampling)
- next next big version 
    * [ ] Support for multiple index
    * [ ] Time series analysis
    * [ ] Optimization

If you like this project, please distribute it and star it for more people to see.
Any suggestions and contributions are very welcomed.

ALL RIGHTS RESERVED
