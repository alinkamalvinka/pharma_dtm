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
End-to-end test for pipeline.
"""

import pytest

from ..src.dtm.kedro_context import get_kedro_context


@pytest.fixture
def context():
    """ pytest fixture to provide the project context """
    return get_kedro_context()


def test_pipeline_run(context):
    """ tests end-to-end pipeline run """
    output = context.run()

    assert set(output.keys()) == {"greeting"}
    assert output["greeting"] == "Hello, user!"
