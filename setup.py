from setuptools import setup

setup(
    name='dshelper',
    version='0.1.0',
    description='A GUI tool to display pandas dataframe and draw plots in a few clicks',
    url='https://github.com/zmcddn/Data-Science-Helper',
    author='Minchang (Carson) Zhang',
    author_email='minchang@ualberta.ca',
    license='MIT',
    packages=[
        'dshelper',
        'dshelper.data',
        'dshelper.plot',
    ],
    install_requires=[
        'wxpython>=3.0',
        'matplotlib>=2.1.2',
        'numpy>=1.14.0',
        'scipy>=1.0.0',
        'pandas>=0.22.0',
        'scikit-learn>=0.19.1',
        'seaborn>=0.8.0',
        'statsmodels>=0.8.0'
    ],
    zip_safe=False
)
