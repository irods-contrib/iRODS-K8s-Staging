# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Job supervisor tests.

    Author: Phil Owen, RENCI.org
"""
import os

import pytest

from src.staging.staging import Staging
from src.common.staging_enums import StagingType


@pytest.mark.skip(reason="Local test only")
def test_run():
    """
    tests doing the normal operations in initial or final staging.

    this test requires that DB connection parameters are set

    :return:
    """
    # init the return value
    ret_val: int = 0

    # create the target class
    staging = Staging()

    # set a run ID
    run_id: str = '0'

    # set up the test directory
    run_dir: str = os.path.join(os.path.dirname(__file__), run_id)

    # make the call to stage
    ret_val = staging.run(run_dir, StagingType.INITIAL_STAGING)

    assert ret_val < 0

    # set a run ID
    run_id: str = '3'

    # set up the test directory
    run_dir: str = os.path.join(os.path.dirname(__file__), run_id)

    # make the call to stage
    ret_val = staging.run(run_dir, StagingType.INITIAL_STAGING)

    # TODO add a test for final staging

    assert ret_val == 0


@pytest.mark.skip(reason="Local test only")
def test_initial_staging():
    """
    tests doing the operations in initial staging.

    Note: this test requires that DB connection parameters are set

    :return:
    """
    # init the return value
    ret_val: int = 0

    # create the target class
    staging = Staging()

    # set up the test conditions
    run_dir: str = os.path.join(os.path.dirname(__file__), '0')

    # set a run ID
    run_id: str = run_dir.split('\\')[-1]

    # call the initial staging method
    ret_val = staging.initial_staging(run_dir, run_id, StagingType.INITIAL_STAGING)

    # check the result. a run id of "0" should fail
    assert ret_val == -1

    # set up the test conditions
    run_dir: str = os.path.join(os.path.dirname(__file__), '3')

    # set a run ID
    run_id: str = run_dir.split('\\')[-1]

    # call the initial staging method
    ret_val = staging.initial_staging(run_dir, run_id, StagingType.INITIAL_STAGING)

    # check the result. a run id of "3" should be ok
    assert ret_val == 0

    # check to make sure the directory and file were create
    assert os.path.isfile(os.path.join(run_dir, 'test_list.json'))


@pytest.mark.skip(reason="Local test only")
def test_final_staging():
    """
    tests doing the operations in final staging.

    Note: this test requires that DB connection parameters are set

    :return:
    """
    # init the return value
    ret_val: int = 0

    # create the target class
    staging = Staging()

    # set up the test conditions
    run_dir: str = os.path.join(os.path.dirname(__file__), '0')

    # set a run ID
    run_id: str = run_dir.split('\\')[-1]

    # call the initial staging method
    ret_val = staging.final_staging(run_dir, run_id, StagingType.INITIAL_STAGING)

    # check the result. a run id of "0" should fail
    assert ret_val == -1

    # set up the test conditions
    run_dir: str = os.path.join(os.path.dirname(__file__), '3')

    # set a run ID
    run_id: str = run_dir.split('\\')[-1]

    # call the initial staging method
    ret_val = staging.initial_staging(run_dir, run_id, StagingType.INITIAL_STAGING)

    # check the result. a run id of "3" should be ok
    assert ret_val == 0

    # check to make sure the directory and file were create
    assert os.path.isfile(os.path.join(run_dir, 'test_list.json'))