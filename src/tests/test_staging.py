# BSD 3-Clause All rights reserved.
#
# SPDX-License-Identifier: BSD 3-Clause

"""
    Job supervisor tests.

    Author: Phil Owen, RENCI.org
"""
import os
from src.staging.staging import Staging
from src.common.staging_enums import StagingType, WorkflowTypeName, ReturnCodes


# @pytest.mark.skip(reason="Local test only")
def test_initial_staging_run():
    """
    tests doing the normal operations for initial staging.

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
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), 'some-dir')

    # make the call to do an initial stage with an invalid run id
    ret_val = staging.run(run_id, run_dir, StagingType.INITIAL_STAGING, WorkflowTypeName.CORE)

    # ensure we got a failure code
    assert ret_val == ReturnCodes.DB_ERROR

    # set a valid run ID
    run_id: str = '1'

    # set up the test directory
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), 'save-this-test-1')

    # make the call to do an initial stage
    ret_val = staging.run(run_id, run_dir, StagingType.INITIAL_STAGING, WorkflowTypeName.CORE)

    # make sure of a successful return code and a bash file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and os.path.isfile(os.path.join(run_dir, run_id, 'PROVIDER_test_list.sh'))

    # make the call to do an initial stage
    ret_val = staging.run(run_id, run_dir, StagingType.INITIAL_STAGING, WorkflowTypeName.CORE)

    # make sure of a successful return code and a bash file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and os.path.isfile(os.path.join(run_dir, run_id, 'PROVIDER_test_list.sh'))

    # make the call to do a final stage. this is an invalid directory and should fail
    ret_val = staging.run(run_id, os.path.join(os.getenv('TEST_PATH'), '0'), StagingType.FINAL_STAGING, WorkflowTypeName.CORE)

    # ensure we got a failure code
    assert ret_val == ReturnCodes.ERROR_NO_RUN_DIR

    # set a valid run ID. however, although this one has an executor specified it has no tests listed in the DB
    run_id: str = '2'

    # set up the test directory
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), 'save-this-test-2')

    # make the call to do an initial stage
    ret_val = staging.run(run_id, run_dir, StagingType.INITIAL_STAGING, WorkflowTypeName.TOPOLOGY)

    # make sure of a successful return code and a bash file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and os.path.isfile(os.path.join(run_dir, run_id, 'CONSUMER_test_list.sh'))


# @pytest.mark.skip(reason="Local test only")
def test_final_staging_run():
    """
    tests doing the normal operations for final staging.

    this test requires that DB connection parameters are set

    :return:
    """
    # init the return value
    ret_val: int = ReturnCodes.EXIT_CODE_SUCCESS

    # create the target class
    staging = Staging()

    # set a valid run ID
    run_id: str = '12'

    # set up the test directory
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), 'save-this-test-12')

    # make the call to do a final stage. this dir was created above so it should be removed
    ret_val = staging.run(run_id, run_dir, StagingType.FINAL_STAGING)

    # make sure of a successful return code and a missing bash file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS  # final no longer removes directories and not os.path.isdir(os.path.join(run_dir, run_id))

    # set a valid run ID. however, although this one has an executor specified it has no tests listed in the DB
    run_id: str = '2'

    # set up the test directory
    run_dir: str = os.path.join(os.getenv('TEST_PATH'), 'save-this-test-2')

    # make the call to do a final stage. this dir was created above so it should be removed
    ret_val = staging.run(run_id, run_dir, StagingType.FINAL_STAGING)

    # make sure of a successful return code and a missing bash file
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS  # final no longer removes directories and not os.path.isdir(os.path.join(run_dir, run_id))


# @pytest.mark.skip(reason="Local test only")
def test_file_creation():
    """
    tests the creation of a file that contains the requested tests

    :return:
    """
    # init the return value
    ret_val: int = ReturnCodes.EXIT_CODE_SUCCESS

    # clear out any previous results
    if os.path.isfile(os.path.join(os.path.dirname(__file__), 'PROVIDER_test_list.sh')):
        os.unlink(os.path.join(os.path.dirname(__file__), 'PROVIDER_test_list.sh'))

    # clear out any previous results
    if os.path.isfile(os.path.join(os.path.dirname(__file__), 'CONSUMER_test_list.sh')):
        os.unlink(os.path.join(os.path.dirname(__file__), 'CONSUMER_test_list.sh'))

    # create the target class
    staging = Staging()

    # create a topology test list with only a provider test declared
    run_data: dict = {"id": 1, "status": "New run accepted for save-this-test-1",
                      "request_data": {"workflow-type": "CORE", "db-image": "postgres:14.11", "db-type": "postgres",
                                       "os-image": "irods-ubuntu-20.04:latest",
                                       "package-dir": "/projects/irods/github-build-artifacts/3957adb/ubuntu:20.04",
                                       "tests": {"PROVIDER": ["test_ihelp"]}}, "request_group": "save-this-test-1"}

    # make the call
    ret_val = staging.create_test_files(os.path.dirname(__file__), run_data, WorkflowTypeName.CORE)

    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and os.path.isfile(os.path.join(os.path.dirname(__file__), 'PROVIDER_test_list.sh'))

    # create a topology test list with only a provider test declared
    run_data: dict = {"id": 2, "status": "New run accepted for save-this-test-1",
                      "request_data": {"workflow-type": "TOPOLOGY", "db-image": "postgres:14.11", "db-type": "postgres",
                                       "os-image": "irods-ubuntu-20.04:latest",
                                       "package-dir": "/projects/irods/github-build-artifacts/3957adb/ubuntu:20.04",
                                       "tests": {"CONSUMER": ["test_ihelp", "test_ils"]}}, "request_group": "save-this-test-1"}

    # make the call
    ret_val = staging.create_test_files(os.path.dirname(__file__), run_data, WorkflowTypeName.TOPOLOGY)

    # check the result
    assert ret_val == ReturnCodes.EXIT_CODE_SUCCESS and os.path.isfile(os.path.join(os.path.dirname(__file__), 'CONSUMER_test_list.sh'))
