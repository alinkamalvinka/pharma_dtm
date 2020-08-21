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
Kedro's project context
"""
from pathlib import Path
from typing import Dict

import kedro.config.default_logger  # noqa, pylint: disable=unused-import
from kedro.context import KedroContext
from kedro.pipeline import Pipeline

from .pipeline import create_pipelines


class ProjectContext(KedroContext):
    """Users can override the remaining methods from the parent class here"""

    project_name = "Dynamic topic modelling pharma"
    project_version = "0.16.4"

    def _get_pipelines(self) -> Dict[str, Pipeline]:
        return create_pipelines()

    def _setup_logging(self):
        pass


def get_kedro_context() -> ProjectContext:
    """
    Provides kedro context for the recipe. Do not copy this over to a real kedro project
    """
    project_root = Path(__file__).parents[2]
    # see https://github.com/quantumblacklabs/private-kedro/issues/229
    return ProjectContext(str(project_root), "base")
