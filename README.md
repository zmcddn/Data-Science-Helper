# Data Science Helper

A visualization tool designed to help data scientists better examine their data sets.

## Feature

* [x] Default view with raw data, dataframe info and describe
* [x] Drag on the header to re-arrange columns
* [x] Left click on the right panel to show/hide columns
* [x] Various plots 
* [x] Bottom right buttons to hide panels and focus on data set
* [x] Dockerized with make commands

## Plots

* [x] Histogram
* [x] Heatmap
* [x] Correlation 
* [x] Scatter Plot
* [x] Box Plot
* [x] Violin Plot
* [x] Pair plot

## Dependencies

* wxpython
* matplotlib
* seaborn
* pandas
* numpy
* sciki-tlearn

## How to run

* `git clone git@github.com:zmcddn/Data-Science-Helper.git`
* `conda create -n py36 python=3.6` or use virtualenv or pipenv
* `activate py36` (windwos) or `source activate py36` (mac, linux)
* `conda install --yes --file requirements.txt` or `pip install -r requirements.txt`
* In case the `PyPubSub` is not installed with conda, you can do `pip install PyPubSub`
* `cd dshelper`
* `python dshelper.py` (windwos, linux) or `pythonw dshelper.py` (mac)

For help with any dataframe, you can follow the following steps:
* `import dshelper`
* `dshelper.help(df)`

## Run with docker

* `make build` to build the project
* `make runlinux` to run in Linux
* WIP for mac

## To-do

* [ ] Sort by columns
* [ ] Support for multiple index
* [ ] More functionalities with datetime column
* [ ] Optimization

Please star my project if you find its useful.
Any suggestions/pull requests are very welcomed.

ALL RIGHTS RESERVED