<div align="center">
  <img height="240px" src="https://docs.google.com/drawings/d/e/2PACX-1vSl80T4MnWRsPX3KvlB2kn6zVdHdUleG_w2zBiLS7RxLGAHxiSYTnw3LZtXh__YMv6KcIOYOvkSt9PB/pub?w=841&h=350" alt="creme_logo"/>
</div>

<div align="center">
  <!-- Travis -->
  <a href="https://travis-ci.org/creme-ml/creme">
    <img src="https://img.shields.io/travis/creme-ml/creme/master.svg?style=for-the-badge" alt="travis" />
  </a>
  <!-- Codecov -->
  <a href="https://codecov.io/gh/creme-ml/creme">
    <img src="https://img.shields.io/codecov/c/gh/creme-ml/creme.svg?style=for-the-badge" alt="codecov" />
  </a>
  <!-- PyPI -->
  <a href="https://pypi.org/project/creme">
    <img src="https://img.shields.io/pypi/v/creme.svg?style=for-the-badge" alt="pypi" />
  </a>
  <!-- License -->
  <a href="https://opensource.org/licenses/BSD-3-Clause">
    <img src="https://img.shields.io/badge/License-BSD%203--Clause-blue.svg?style=for-the-badge" alt="bsd_3_license"/>
  </a>
</div>

<br/>

`creme` is a library for online machine learning, also known as in**creme**ntal learning. Online learning is a machine learning regime where a model learns one observation at a time. This is in contrast to batch learning where all the data is processed in one go. Incremental learning is desirable when the data is too big to fit in memory, or simply when you want to handle data in a streaming fashion. In addition to many online machine learning algorithms, `creme` provides utilities for extracting features from a stream of data. The API is heavily inspired from that of [scikit-learn](https://scikit-learn.org/stable/), meaning that users who are familiar with it should feel comfortable.

## Useful links

- [Documentation](https://creme-ml.github.io/)
  - [API reference](https://creme-ml.github.io/api.html)
  - [User guide](https://creme-ml.github.io/user-guide.html)
  - [FAQ](https://creme-ml.github.io/faq.html)
- [Issue tracker](https://github.com/creme-ml/creme/issues)
- [Package releases](https://pypi.org/project/creme/#history)
- [Change history](CHANGELOG.md)
- PyData Amsterdam 2019 presentation ([slides](https://maxhalford.github.io/slides/creme-pydata/), [video](https://www.youtube.com/watch?v=P3M6dt7bY9U&list=PLGVZCDnMOq0q7_6SdrC2wRtdkojGBTAht&index=11))
- [Toulouse Data Science presentation](https://maxhalford.github.io/slides/creme-tds/)
- [Blog post from pyimagesearch for image classification](https://www.pyimagesearch.com/2019/06/17/online-incremental-learning-with-keras-and-creme/)

## Installation

:point_up: `creme` is intended to work with Python 3.6 and above.

`creme` can simply be installed with `pip`.

    pip install creme

You can also install the latest development version as so:

    pip install git+https://github.com/creme-ml/creme --upgrade

As for dependencies, `creme` mostly relies on Python's standard library. Sometimes it relies on `numpy`, `scipy`, and `scikit-learn` to avoid reinventing the wheel.

## Quick example

In the following example we'll use a linear regression to forecast the number of available bikes in [bike stations](https://www.wikiwand.com/en/Bicycle-sharing_system) from the city of Toulouse :bike:.

We'll use the available numeric features, as well as calculate running averages of the target. Before being fed to the linear regression, the features will be scaled using a `StandardScaler`. Note that each of these steps works in a streaming fashion, including the feature extraction. We'll evaluate the model by asking it to forecast 30 minutes ahead while delaying the true answers, which ensures that we're simulating a production scenario. Finally we will print the current score every 20,000 predictions.

```python
>>> import datetime as dt
>>> from creme import compose
>>> from creme import datasets
>>> from creme import feature_extraction
>>> from creme import linear_model
>>> from creme import metrics
>>> from creme import model_selection
>>> from creme import preprocessing
>>> from creme import stats

>>> X_y = datasets.fetch_bikes()

>>> def add_hour(x):
...     x['hour'] = x['moment'].hour
...     return x

>>> model = compose.Whitelister('clouds', 'humidity', 'pressure', 'temperature', 'wind')
>>> model += (
...     add_hour |
...     feature_extraction.TargetAgg(by=['station', 'hour'], how=stats.Mean())
... )
>>> model += feature_extraction.TargetAgg(by='station', how=stats.EWMean(0.5))
>>> model |= preprocessing.StandardScaler()
>>> model |= linear_model.LinearRegression()

>>> model_selection.online_qa_score(
...     X_y=X_y,
...     model=model,
...     metric=metrics.MAE(),
...     on='moment',
...     lag=dt.timedelta(minutes=30),
...     print_every=30_000
... )
[30,000] MAE: 2.193069
[60,000] MAE: 2.249345
[90,000] MAE: 2.288321
[120,000] MAE: 2.265257
[150,000] MAE: 2.2674
[180,000] MAE: 2.282485
MAE: 2.285921

```

We can also draw the model to understand how the data flows through.

```python
>>> dot = model.draw()

```

<div align="center">
  <img src="docs/_static/bikes_pipeline.svg" alt="bikes_pipeline"/>
</div>

By only using a few lines of code, we've built a robust model and evaluated it by simulating a production scenario. You can find a more detailed version of this example [here](https://creme-ml.github.io/notebooks/bike-sharing-forecasting.html). `creme` is a framework that has a lot to offer, and as such we kindly refer you to the [documentation](https://creme-ml.github.io/) if you want to know more.

## Benchmarks

All the benchmarks, including reproducible code, are available [here](benchmarks).

The following table summarizes the performance of regression methods from various libraries, using their default parameters.

<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Library</th>
      <th>Model</th>
      <th>MSE</th>
      <th>Fit time</th>
      <th>Average fit time</th>
      <th>Predict time</th>
      <th>Average predict time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>creme</td>
      <td><code>LinearRegression</code></td>
      <td>118.549437</td>
      <td>2s, 580ms</td>
      <td>10μs</td>
      <td>759ms</td>
      <td>3μs</td>
    </tr>
    <tr>
      <td>creme</td>
      <td><code>PARegressor</code></td>
      <td>143.477210</td>
      <td>6s, 994ms</td>
      <td>27μs</td>
      <td>1s, 305ms</td>
      <td>5μs</td>
    </tr>
    <tr>
      <td>creme</td>
      <td><code>KNeighborsRegressor</code></td>
      <td>155.585250</td>
      <td>394ms</td>
      <td>1μs</td>
      <td>37s, 4ms</td>
      <td>146μs</td>
    </tr>
    <tr>
      <td>scikit-learn</td>
      <td><code>SGDRegressor</code></td>
      <td>120.185848</td>
      <td>36s, 433ms</td>
      <td>144μs</td>
      <td>14s, 766ms</td>
      <td>58μs</td>
    </tr>
    <tr>
      <td>scikit-learn</td>
      <td><code>PassiveAggressiveRegressor</code></td>
      <td>143.477210</td>
      <td>35s, 551ms</td>
      <td>141μs</td>
      <td>14s, 599ms</td>
      <td>57μs</td>
    </tr>
    <tr>
      <td>PyTorch (CPU)</td>
      <td><code>Linear</code></td>
      <td>142.495995</td>
      <td>47s, 335ms</td>
      <td>187μs</td>
      <td>14s, 822ms</td>
      <td>58μs</td>
    </tr>
    <tr>
      <td>Keras on Tensorflow (CPU)</td>
      <td><code>Dense</td>
      <td>142.494512</td>
      <td>1m, 18s, 296ms</td>
      <td>310μs</td>
      <td>49s, 225ms</td>
      <td>195μs</td>
    </tr>
    <tr>
      <td>scikit-garden</td>
      <td><code>MondrianTreeRegressor</code></td>
      <td>201.687033</td>
      <td>35s, 983ms</td>
      <td>142μs</td>
      <td>23s, 502ms</td>
      <td>93μs</td>
    </tr>
    <tr>
      <td>scikit-garden</td>
      <td><code>MondrianForestRegressor</code></td>
      <td>142.364156</td>
      <td>5m, 58s, 226ms</td>
      <td>1ms, 420μs</td>
      <td>2m, 40s, 728ms</td>
      <td>637μs</td>
    </tr>
  </tbody>
</table>

## Contributing

Like many subfields of machine learning, online learning is far from being an exact science and so there is still a lot to do. Feel free to contribute in any way you like, we're always open to new ideas and approaches. If you want to contribute to the code base please check out the [`CONTRIBUTING.md` file](CONTRIBUTING.md). Also take a look at the [issue tracker](https://github.com/creme-ml/creme/issues) and see if anything takes your fancy.

Last but not least you are more than welcome to share with us on how you're using `creme` or online learning in general! We believe that online learning solves a lot of pain points in practice, and would love to share experiences.

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind are welcome!

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore -->
<table>
  <tr>
    <td align="center"><a href="https://maxhalford.github.io"><img src="https://avatars1.githubusercontent.com/u/8095957?v=4" width="100px;" alt="Max Halford"/><br /><sub><b>Max Halford</b></sub></a><br /><a href="#projectManagement-MaxHalford" title="Project Management">📆</a> <a href="https://github.com/Max Halford/creme/commits?author=MaxHalford" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/AdilZouitine"><img src="https://avatars0.githubusercontent.com/u/24889239?v=4" width="100px;" alt="AdilZouitine"/><br /><sub><b>AdilZouitine</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=AdilZouitine" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/raphaelsty"><img src="https://avatars3.githubusercontent.com/u/24591024?v=4" width="100px;" alt="Raphael Sourty"/><br /><sub><b>Raphael Sourty</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=raphaelsty" title="Code">💻</a></td>
    <td align="center"><a href="http://www.linkedin.com/in/gbolmier"><img src="https://avatars0.githubusercontent.com/u/25319692?v=4" width="100px;" alt="Geoffrey Bolmier"/><br /><sub><b>Geoffrey Bolmier</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=gbolmier" title="Code">💻</a></td>
    <td align="center"><a href="http://koaning.io"><img src="https://avatars1.githubusercontent.com/u/1019791?v=4" width="100px;" alt="vincent d warmerdam "/><br /><sub><b>vincent d warmerdam </b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=koaning" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/VaysseRobin"><img src="https://avatars2.githubusercontent.com/u/32324822?v=4" width="100px;" alt="VaysseRobin"/><br /><sub><b>VaysseRobin</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=VaysseRobin" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/tweakyllama"><img src="https://avatars0.githubusercontent.com/u/7049400?v=4" width="100px;" alt="Lygon Bowen-West"/><br /><sub><b>Lygon Bowen-West</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=tweakyllama" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/flegac"><img src="https://avatars2.githubusercontent.com/u/4342302?v=4" width="100px;" alt="Florent Le Gac"/><br /><sub><b>Florent Le Gac</b></sub></a><br /><a href="https://github.com/Max Halford/creme/commits?author=flegac" title="Code">💻</a></td>
    <td align="center"><a href="http://www.pyimagesearch.com"><img src="https://avatars2.githubusercontent.com/u/759645?v=4" width="100px;" alt="Adrian Rosebrock"/><br /><sub><b>Adrian Rosebrock</b></sub></a><br /><a href="#blog-jrosebr1" title="Blogposts">📝</a></td>
  </tr>
</table>

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License

See the [license file](LICENSE).
