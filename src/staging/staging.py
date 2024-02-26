# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

"""
    Main entry point for the staging microservice application
"""
import os
import json
import shutil
import sys

from src.common.logger import LoggingUtil
from src.common.pg_impl import PGImplementation
from src.common.staging_enums import StagingType, StagingTestExecutor, WorkflowTypeName, ReturnCodes


class Staging:
    """
    Class that contains functionality for staging

    """

    def __init__(self):
        # get the app version
        self.app_version: str = os.getenv('APP_VERSION', 'Version number not set')

        # get the environment this instance is running on
        self.system: str = os.getenv('SYSTEM', 'System name not set')

        # get the log level and directory from the environment.
        log_level, log_path = LoggingUtil.prep_for_logging()

        # create a logger
        self.logger = LoggingUtil.init_logging("iRODS.Staging", level=log_level, line_format='medium', log_file_path=log_path)

        # specify the DB to get a connection
        # note the extra comma makes this single item a singleton tuple
        db_names: tuple = ('irods-sv',)

        # create a DB connection object
        self.db_info: PGImplementation = PGImplementation(db_names, _logger=self.logger)

    def run(self, run_id: str, run_dir: str, step_type: StagingType, workflow_type: WorkflowTypeName = WorkflowTypeName.CORE) -> int:
        """
        Performs the requested type of staging operation.

        The supervisor will mount the /data directory for this component by default.

        :param run_id: The id of the run.
        :param run_dir: The base path of the directory to use for the staging operations.
        :param step_type: The type of staging step, either 'initial' or 'final'
        :param workflow_type:

        :return:
        """
        # init the return value
        ret_val: int = ReturnCodes.EXIT_CODE_SUCCESS

        # is this an initial stage step?
        if step_type == StagingType.INITIAL_STAGING:
            # make the call to perform the op
            ret_val = self.initial_staging(run_id, run_dir, step_type, workflow_type)
        # else this a final stage step
        elif step_type == StagingType.FINAL_STAGING:
            # make the call to perform the op
            ret_val = self.final_staging(run_id, run_dir, step_type)

        # return to the caller
        return ret_val

    def initial_staging(self, run_id: str, run_dir: str, staging_type: StagingType, workflow_type: WorkflowTypeName) -> int:
        """
        Performs the initial staging

        :param run_id: The ID of the supervisor run request.
        :param run_dir: The path of the directory to use for the staging operations.
        :param staging_type: The type of staging step, either 'initial' or 'final'
        :param workflow_type: the type of workflow

        :return:
        """
        # init the return code
        ret_val: int = ReturnCodes.EXIT_CODE_SUCCESS

        self.logger.info('Initial staging version %s start: run_id: %s, run_dir: %s, workflow type: %s', self.app_version, run_id, run_dir,
                         workflow_type)

        try:
            # try to make the call for records
            run_data: json = self.db_info.get_run_def(run_id)

            # did getting the data to go ok
            if run_data != -1:
                # remove the run directory, ignore errors as it may not exist
                shutil.rmtree(run_dir, ignore_errors=True)

                # make the directory
                os.makedirs(run_dir)

                # make sure the directory has the correct permissions
                if sys.platform != 'win32':
                    os.chmod(run_dir, 0o777)

                # if there are tests requested, create the files
                if 'tests' in run_data['request_data']:
                    # create the test file(s)
                    ret_val = self.create_test_files(run_dir, run_data, workflow_type)
            else:
                # set the return value
                ret_val = run_data

        except Exception:
            # declare ready
            self.logger.exception('Exception: The iRODS K8s "%s" staging request for run directory %s failed.', staging_type, run_dir)

            # set the exception error code
            ret_val = ReturnCodes.EXCEPTION_RUN_PROCESSING

        self.logger.info('Initial staging complete: run_dir: %s, ret_val: %s', run_dir, ret_val)

        # return the result to the caller
        return ret_val

    def create_test_files(self, run_dir: str, run_data: json, workflow_type: WorkflowTypeName) -> int:
        """
        Creates the files that contain the requested test executor and tests.

        :param run_dir: The path of the directory to use for the staging operations.
        :param run_data: The run data information from the supervisor
        :param workflow_type: the type of workflow

        :return:
        """
        # init the return
        ret_val: int = ReturnCodes.EXIT_CODE_SUCCESS

        # init the filename storage
        out_file_name: str = 'empty'

        self.logger.info('Creating test files. run_dir: %s, workflow type: %s', run_dir, workflow_type)

        try:
            # for each test in the list
            for item in run_data['request_data']['tests']:
                # get the name of the executor type for the tests
                executor = list(item)[0]

                # is this a legit executor?
                if executor in StagingTestExecutor.__members__:
                    # get the list of tests for this executor
                    tests = list(item.values())[0]

                    # check the list of tests
                    if len(tests) > 0:
                        # generate the output path/file name
                        out_file_name = os.path.join(run_dir, f'{executor}_test_list.sh')

                        # write out the data
                        with open(out_file_name, 'w', encoding='utf-8') as fp:
                            self.logger.debug('Writing to %s', out_file_name)

                            # write out the preamble
                            fp.write('#/bin/bash\ncd /var/lib/irods;\n')

                            # init the base command line.
                            base_cmd_line: str = ''

                            # init the topology test type
                            topology_test_type: str = ''

                            # get the command line
                            if workflow_type == WorkflowTypeName.CORE:
                                # assign the base command line
                                base_cmd_line = 'python3 scripts/run_tests.py --xml_output'
                            elif workflow_type == WorkflowTypeName.TOPOLOGY:
                                # assign the base command line
                                base_cmd_line = 'python3 scripts/run_tests.py --xml_output --hostnames TEST_HOST_NAMES --topology '

                                # if this is a provider instance type
                                if executor in [StagingTestExecutor.PROVIDER.name, StagingTestExecutor.PROVIDERSECONDARY.name]:
                                    # get the topology test type
                                    topology_test_type = 'icat'
                                # else it is a consumer instance type
                                elif executor in [StagingTestExecutor.CONSUMER.name, StagingTestExecutor.CONSUMERSECONDARY.name,
                                                  StagingTestExecutor.CONSUMERTERTIARY.name]:
                                    # get the topology test type
                                    topology_test_type = 'resource'

                            # write out each test listed in the request
                            for test in tests:
                                # create the test entry with some extra info
                                fp.write(f'echo "Running {test}"; {base_cmd_line}{topology_test_type} --run_s {test};\n')

                            # declare the testing complete
                            fp.write(f'echo "Copying /var/lib/irods/test-report/ results..."; cp ./test-reports/*.xml {run_dir};\n')

                            # save these directories for extended forensics
                            fp.write(f'echo "Moving /var/lib/irods/log dir..."; mv ./log {run_dir};\n')
                            fp.write(f'echo "Moving /var/log/irods/ dir..."; mv /var/log/irods/ {run_dir};\n')

                        # make sure the file has the correct permissions
                        if sys.platform != 'win32':
                            os.chmod(out_file_name, 0o777)

                    else:
                        self.logger.debug('WARNING: An executor was specified with no tests. executor name %s, run_dir: %s, workflow type: %s',
                                          executor, run_dir, workflow_type.name)
                else:
                    self.logger.debug('WARNING: Invalid or missing executor. name: %s, run_dir: %s, workflow type: %s', executor, run_dir,
                                      workflow_type.name)

        except Exception:
            # declare ready
            self.logger.exception('Exception: Error creating the test file: %s.', out_file_name)

            # set the return
            ret_val = ReturnCodes.ERROR_TEST_FILE

        # return to the caller
        return ret_val

    def final_staging(self, run_id: str, run_dir: str, staging_type: StagingType) -> int:
        """
        Performs the initial staging

        :param run_dir: The path of the directory to use for the staging operations.
        :param run_id: The ID of the supervisor run request.
        :param staging_type: The type of staging step, either 'initial' or 'final'
        :return:
        """
        # init the return code
        ret_val: int = ReturnCodes.EXIT_CODE_SUCCESS

        self.logger.info('Final staging version %s start: run_dir: %s', self.app_version, run_dir)

        try:
            # does the directory exist?
            if os.path.isdir(run_dir):
                # try to make the call for records
                run_data: json = self.db_info.get_run_def(run_id)

                # did getting the data to go ok
                if run_data != ReturnCodes.DB_ERROR:
                    # get the grouping value from the request
                    run_group: str = run_data['request_group']

                    # get the target directory
                    dest_dir = run_dir.replace(run_id, run_group)

                    # remove the dest directory
                    shutil.rmtree(dest_dir, ignore_errors=True)

                    # move the source directory to the dest
                    shutil.move(run_dir, dest_dir)
            else:
                # set a failure return code for no run directory
                ret_val = ReturnCodes.ERROR_NO_RUN_DIR
        except Exception:
            # declare ready
            self.logger.exception('Exception: The iRODS K8s "%s" final staging request for run directory %s failed.', staging_type, run_dir)

            # set the exception error code
            ret_val = ReturnCodes.EXCEPTION_RUN_PROCESSING

        self.logger.info('Final staging complete: run_dir: %s, ret_val: %s', run_dir, ret_val)

        # return the result to the caller
        return ret_val
