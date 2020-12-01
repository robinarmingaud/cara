import dataclasses

import pytest
import numpy.testing as npt

from cara import models


@pytest.fixture
def baseline_slidingwindow():
    return models.SlidingWindow(
            active=models.SpecificInterval(((0, 4), (5, 9))),
            inside_temp=models.PiecewiseConstant((0, 24), (293,)),
            outside_temp=models.PiecewiseConstant((0, 24), (283,)),
            window_height=1.6, opening_length=0.6,
        )


@pytest.fixture
def baseline_hingedwindow():
    return models.HingedWindow(
            active=models.SpecificInterval(((0, 4), (5, 9))),
            inside_temp=models.PiecewiseConstant((0, 24), (293,)),
            outside_temp=models.PiecewiseConstant((0, 24), (283,)),
            window_height=1.6, opening_length=0.6, window_width=1.,
        )


def test_number_of_windows(baseline_slidingwindow):
    room = models.Room(75)
    two_windows = dataclasses.replace(baseline_slidingwindow, number_of_windows=2)

    one_window_exchange = baseline_slidingwindow.air_exchange(room, 1)
    two_window_exchange = two_windows.air_exchange(room, 1)
    assert one_window_exchange != 0
    assert one_window_exchange * 2 == two_window_exchange


@pytest.mark.parametrize(
    "window_width, expected_cd_b",
    [
        [0.5, 0.01369640075],
        [1., 0.01056914747],
        [2., 0.00843150922],
        [4., 0.00779945967],
    ],
)
def test_hinged_window(baseline_hingedwindow,window_width,expected_cd_b):
    room = models.Room(75)
    hinged_window = dataclasses.replace(baseline_hingedwindow,
                                        window_width=window_width)

    npt.assert_allclose(hinged_window.cd_b, expected_cd_b, rtol=1e-8)


def test_sliding_window(baseline_slidingwindow):
    room = models.Room(75)

    assert baseline_slidingwindow.cd_b == 0.6
