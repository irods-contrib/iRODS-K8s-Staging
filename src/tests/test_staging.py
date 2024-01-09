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
    tests doing the normal operations for initial and final staging.

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
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), run_id)

    # make the call to do an initial stage
    ret_val = staging.run(run_dir, StagingType.INITIAL_STAGING)

    # ensure we got a failure code
    assert ret_val < 0

    # set a run ID
    run_id: str = '3'

    # set up the test directory
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), run_id)

    # make the call to do an initial stage
    ret_val = staging.run(run_dir, StagingType.INITIAL_STAGING)

    # make sure of a successful return code and a json file
    assert ret_val == 0 and os.path.isfile(os.path.join(run_dir, 'test_list.json'))

    # make the call to do a final stage. this invalid directory should fail
    ret_val = staging.run('//', StagingType.FINAL_STAGING)

    # ensure we got a failure code
    assert ret_val < 0

    # make the call to do a final stage. this dir was created above so it should be removed
    ret_val = staging.run(run_dir, StagingType.FINAL_STAGING)

    # make sure of a successful return code and a missing json file
    assert ret_val == 0 and not os.path.isdir(run_dir)


def test_file_creation():
    """
    tests the creation of a file that contains the requested tests

    :return:
    """
    # init the return value
    ret_val: int = 0

    # create the target class
    staging = Staging()

    # create a test list
    run_data: dict = {'request_data': {"workflow-type": "CORE", "os-image": "ubuntu-20.04:latest", "test-image": "busybox:1.35",
                                       "tests": [{'CONSUMER': ["test_ihelp", "test_ilocate", "test_ils"]},
                                                 {'PROVIDER': ["test_ihelp", "test_ilocate", "test_ils"]}]}}

    # make the call
    ret_val = staging.create_test_files(os.path.dirname(__file__), run_data)

    # check the result
    assert ret_val == 0 and os.path.isfile(os.path.join(os.path.dirname(__file__), 'consumer_test_list.json')) and os.path.isfile(
        os.path.join(os.path.dirname(__file__), 'provider_test_list.json'))

    # remove the files created
    os.unlink(os.path.join(os.path.dirname(__file__), 'consumer_test_list.json'))
    os.unlink(os.path.join(os.path.dirname(__file__), 'provider_test_list.json'))

    run_data: dict = {'request_data': {'workflow-type': 'CORE', 'os-image': 'ubuntu-20.04:latest', 'test-image': 'busybox:1.35',
                                       'tests': [{'CONSUMER': ["test_ihelp", "test_ilocate", "test_ils"]}]}}

    # make the call
    ret_val = staging.create_test_files(os.path.dirname(__file__), run_data)

    # check the result
    assert ret_val == 0 and os.path.isfile(os.path.join(os.path.dirname(__file__), 'consumer_test_list.json')) and not os.path.isfile(
        os.path.join(os.path.dirname(__file__), 'provider_test_list.json'))
