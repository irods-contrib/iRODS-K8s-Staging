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
from src.common.staging_enums import StagingType, WorkflowTypeName, ReturnCodes


@pytest.mark.skip(reason="Local test only")
def test_run():
    """
    tests doing the normal operations for initial and final staging.

    this test requires that DB connection parameters are set

    :return:
    """
    # init the return value
    ret_val: int = ReturnCodes.EXIT_CODE_SUCCESS

    # create the target class
    staging = Staging()

    # set a run ID
    run_id: str = '0'

    # set up the test directory
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), run_id)

    # make the call to do an initial stage with an invalid run id
    ret_val = staging.run(run_dir, StagingType.INITIAL_STAGING, WorkflowTypeName.CORE)

    # ensure we got a failure code
    assert ret_val == ReturnCodes.DB_ERROR

    # set a valid run ID
    run_id: str = '3'

    # set up the test directory
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), run_id)

    # make the call to do an initial stage
    ret_val = staging.run(run_dir, StagingType.INITIAL_STAGING, WorkflowTypeName.TOPOLOGY)

    # make sure of a successful return code and a json file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and os.path.isfile(os.path.join(run_dir, 'PROVIDER_test_list.sh'))

    # make the call to do a final stage. this dir was created above so it should be removed
    ret_val = staging.run(run_dir, StagingType.FINAL_STAGING)

    # make sure of a successful return code and a missing json file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and not os.path.isdir(run_dir)

    # make the call to do an initial stage
    ret_val = staging.run(run_dir, StagingType.INITIAL_STAGING, WorkflowTypeName.CORE)

    # make sure of a successful return code and a json file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and os.path.isfile(os.path.join(run_dir, 'PROVIDER_test_list.sh'))

    # make the call to do a final stage. this is an invalid directory and should fail
    ret_val = staging.run(os.path.join(os.getenv('TEST_PATH'), '0'), StagingType.FINAL_STAGING, WorkflowTypeName.CORE)

    # ensure we got a failure code
    assert ret_val == ReturnCodes.ERROR_NO_RUN_DIR

    # make the call to do a final stage. this dir was created above so it should be removed
    ret_val = staging.run(run_dir, StagingType.FINAL_STAGING)

    # make sure of a successful return code and a missing json file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and not os.path.isdir(run_dir)

    # set a valid run ID. however, although this one has an executor specified it has no tests listed
    run_id: str = '9'

    # set up the test directory
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), run_id)

    # make the call to do an initial stage
    ret_val = staging.run(run_dir, StagingType.INITIAL_STAGING, WorkflowTypeName.CORE)

    # make sure of a successful return code and a json file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and not os.path.isfile(os.path.join(run_dir, 'PROVIDER_test_list.sh'))

    # make the call to do a final stage. this dir was created above so it should be removed
    ret_val = staging.run(run_dir, StagingType.FINAL_STAGING)

    # make sure of a successful return code and a missing json file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and not os.path.isdir(run_dir)


@pytest.mark.skip(reason="Local test only")
def test_file_creation():
    """
    tests the creation of a file that contains the requested tests

    :return:
    """
    # init the return value
    ret_val: int = ReturnCodes.EXIT_CODE_SUCCESS

    # create the target class
    staging = Staging()

    # create a test list
    run_data: dict = {"request_data": {"workflow-type": "CORE", "os-image": "ubuntu-20.04:latest", "test-image": "busybox:1.35",
                                       "tests": [{"CONSUMER": ["test_ihelp", "test_ilocate", "test_ils"]},
                                                 {"PROVIDER": ["test_ihelp", "test_ilocate", "test_ils"]}]}}

    # make the call
    ret_val = staging.create_test_files(os.path.dirname(__file__), run_data, WorkflowTypeName.CORE)

    # check the result
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and os.path.isfile(
        os.path.join(os.path.dirname(__file__), 'CONSUMER_test_list.sh')) and os.path.isfile(
        os.path.join(os.path.dirname(__file__), 'PROVIDER_test_list.sh'))

    # remove the files created
    os.unlink(os.path.join(os.path.dirname(__file__), 'CONSUMER_test_list.sh'))
    os.unlink(os.path.join(os.path.dirname(__file__), 'PROVIDER_test_list.sh'))

    run_data: dict = {"request_data": {"workflow-type": "CORE", "os-image": "ubuntu-20.04:latest", "test-image": "busybox:1.35",
                                       "tests": [{"CONSUMER": ["test_ihelp", "test_ilocate", "test_ils"]}]}}

    # make the call
    ret_val = staging.create_test_files(os.path.dirname(__file__), run_data, WorkflowTypeName.CORE)

    # check the result
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and os.path.isfile(
        os.path.join(os.path.dirname(__file__), 'CONSUMER_test_list.sh')) and not os.path.isfile(
        os.path.join(os.path.dirname(__file__), 'PROVIDER_test_list.sh'))
