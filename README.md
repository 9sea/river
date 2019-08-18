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
  <!-- Codacy -->
  <a href="https://www.codacy.com/app/MaxHalford/creme">
    <img src="https://img.shields.io/codacy/grade/56da6d188f4a417da0b7eaa435303862.svg?style=for-the-badge" alt="codecov" />
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
[30,000] MAE: 2.178272
[60,000] MAE: 2.252304
[90,000] MAE: 2.295292
[120,000] MAE: 2.273231
[150,000] MAE: 2.274828
[180,000] MAE: 2.291274
MAE: 2.295017

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

The following results compare different implementations of linear regression trained with plain stochastic gradient descent. We used the bikes dataset and measured the mean squared error (MSE). We also measured the time taken for updating each model as well as for making predictions.

<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Library</th>
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
      <td>23.035085</td>
      <td>1s, 636ms</td>
      <td>8μs, 970ns</td>
      <td>516ms, 695μs</td>
      <td>2μs, 832ns</td>
    </tr>
    <tr>
      <td>scikit-learn</td>
      <td>25.295369</td>
      <td>22s, 777ms</td>
      <td>124μs, 827ns</td>
      <td>9s, 235ms</td>
      <td>50μs, 612ns</td>
    </tr>
    <tr>
      <td>PyTorch (CPU)</td>
      <td>23.035086</td>
      <td>35s, 24ms</td>
      <td>191μs, 947ns</td>
      <td>12s, 133ms</td>
      <td>66μs, 494ns</td>
    </tr>
    <tr>
      <td>Keras on Tensorflow (CPU)</td>
      <td>23.035086</td>
      <td>50s, 929ms</td>
      <td>279μs, 114ns</td>
      <td>32s, 616ms</td>
      <td>178μs, 748ns</td>
    </tr>
  </tbody>
</table>

`creme` produces the same MSE as the rest of the libraries. Note that the single reason why scikit-learn is slightly worse is because it has a different squared loss convention – that is, it uses `0.5 * (y_true - y_pred) ** 2` instead of `(y_true - y_pred) ** 2`. Meanwhile, `creme` is an order of magnitude faster than other libraries, for the simple reason that it is a pure online learning library, whereas other libraries are focused on (mini) batch learning.

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
