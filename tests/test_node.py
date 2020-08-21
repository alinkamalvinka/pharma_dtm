# QUANTUMBLACK CONFIDENTIAL
#
# Copyright (c) 2016 - present QuantumBlack Visual Analytics Ltd. All
# Rights Reserved.
#
# NOTICE: All information contained herein is, and remains the property of
# QuantumBlack Visual Analytics Ltd. and its suppliers, if any. The
# intellectual and technical concepts contained herein are proprietary to
# QuantumBlack Visual Analytics Ltd. and its suppliers and may be covered
# by UK and Foreign Patents, patents in process, and are protected by trade
# secret or copyright law. Dissemination of this information or
# reproduction of this material is strictly forbidden unless prior written
# permission is obtained from QuantumBlack Visual Analytics Ltd.
"""
Unit tests for node.
"""

import pytest

from ..src.dtm.nodes.greeting import say_hello


@pytest.mark.parametrize(
    "name,expected", [("Max", "Hello, Max!"), ("Lisa", "Hello, Lisa!")]
)
def test_output(name, expected):
    output = say_hello(name)
    assert output == expected


def test_wrong_input():
    with pytest.raises(ValueError, match="`name` must be a string. Got `int`."):
        say_hello(42)
