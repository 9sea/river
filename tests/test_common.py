"""
General tests for all estimators.
"""
import copy
import pytest

from sklearn.utils import estimator_checks

from creme import cluster
from creme import compat
from creme import feature_selection
from creme import linear_model
from creme import multiclass
from creme import naive_bayes
from creme import preprocessing
from creme import stats
from creme import utils


ESTIMATORS = [
    naive_bayes.GaussianNB(),
    preprocessing.StandardScaler(),
    cluster.KMeans(n_clusters=5, random_state=42),
    preprocessing.MinMaxScaler(),
    preprocessing.MinMaxScaler() + preprocessing.StandardScaler(),
    preprocessing.PolynomialExtender(),
    feature_selection.VarianceThreshold(),
    feature_selection.SelectKBest(similarity=stats.PearsonCorrelation())
]


@pytest.mark.parametrize(
    'estimator',
    [pytest.param(copy.deepcopy(estimator), id=str(estimator)) for estimator in ESTIMATORS]
)
def test_sklearn_check_estimator(estimator):
    estimator_checks.check_estimator(compat.convert_creme_to_sklearn(estimator))


@pytest.mark.parametrize(
    'estimator',
    [
        pytest.param(copy.deepcopy(estimator), id=str(estimator))
        for estimator in ESTIMATORS + [
            # sklearn's check_estimator doesn't binary classifiers yet
            linear_model.LogisticRegression(),
            # sklearn's check_estimator doesn't support pipelines yet
            preprocessing.StandardScaler() | linear_model.LinearRegression(),
            preprocessing.StandardScaler() | linear_model.PAClassifier(),
            preprocessing.StandardScaler() | multiclass.OneVsRestClassifier(linear_model.LogisticRegression()),
            preprocessing.StandardScaler() | multiclass.OneVsRestClassifier(linear_model.PAClassifier()),
        ]
    ]
)
def test_creme_check_estimator(estimator):
    utils.check_estimator(estimator)
