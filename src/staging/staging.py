# BSD 3-Clause All rights reserved.
#
# SPDX-License-Identifier: BSD 3-Clause

"""
    Main entry point for the staging microservice application
"""
import os
import json
import shutil
import sys
import glob

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

        # get the default iRODS package directory
        self.default_pkg_dir = os.getenv('DEFAULT_PKG_DIR', '')

    def run(self, run_id: str, run_dir: str, step_type: StagingType, workflow_type: WorkflowTypeName = WorkflowTypeName.CORE) -> ReturnCodes:
        """
        Performs the requested type of staging operation.

        The supervisor will mount the /data directory for this component by default.

        :param run_id: The id of the run.
        :param run_dir: The base path of the directory to use for the staging operations.
        :param step_type: The type of staging step, either 'initial' or 'final'.
        :param workflow_type: The type of workflow.

        :return:
        """
        # init the return value
        ret_val: ReturnCodes = ReturnCodes.EXIT_CODE_SUCCESS

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

    def initial_staging(self, run_id: str, run_dir: str, staging_type: StagingType, workflow_type: WorkflowTypeName) -> ReturnCodes:
        """
        Performs the initial staging

        :param run_id: The ID of the supervisor run request.
        :param run_dir: The base path of the directory to use for the staging operations.
        :param staging_type: The type of staging step, either 'initial' or 'final'.
        :param workflow_type: The type of workflow.

        :return:
        """
        # init the return code
        ret_val: ReturnCodes = ReturnCodes.EXIT_CODE_SUCCESS

        self.logger.info('Initial staging version %s start: run_id: %s, run_dir: %s, workflow type: %s', self.app_version, run_id, run_dir,
                         workflow_type)

        try:
            # create the full run directory name
            new_run_dir = os.path.join(run_dir, run_id)

            # try to make the call for records
            run_data: json = self.db_info.get_run_def(run_id)

            # did getting the data to go ok
            if run_data != -1:
                # remove the run directory, ignore errors as it may not exist
                shutil.rmtree(new_run_dir, ignore_errors=True)

                # remove zip files from previous runs
                for file in glob.glob(os.path.join(run_dir, '*.zip')):
                    # remove the file
                    os.unlink(file)

                # also clear out any previous test results
                self.db_info.update_run_results(run_id, None)

                # make the directory
                os.makedirs(new_run_dir)

                # make sure the directory has the correct permissions
                if sys.platform != 'win32':
                    os.chmod(new_run_dir, 0o777)

                # if there are tests requested, create the files
                if 'tests' in run_data['request_data']:
                    # create the test file(s)
                    ret_val = self.create_test_files(new_run_dir, run_data, workflow_type)
            else:
                # set the return value
                ret_val = ReturnCodes.DB_ERROR

        except Exception:
            # declare ready
            self.logger.exception('Exception: The iRODS K8s "%s" staging request for run directory %s failed.', staging_type, new_run_dir)

            # set the exception error code
            ret_val = ReturnCodes.EXCEPTION_RUN_PROCESSING

        self.logger.info('Initial staging complete: run_dir: %s, ret_val: %s', new_run_dir, ret_val)

        # return the result to the caller
        return ret_val

    def create_test_files(self, run_dir: str, run_data: json, workflow_type: WorkflowTypeName) -> ReturnCodes:
        """
        Creates the files that contain the requested test executor and tests.

        :param run_dir: The path of the directory to use for the staging operations.
        :param run_data: The run data information from the supervisor.
        :param workflow_type: The type of workflow.

        :return:
        """
        # init the return
        ret_val: ReturnCodes = ReturnCodes.EXIT_CODE_SUCCESS

        # init the filename storage
        out_file_name: str = 'empty'

        self.logger.info('Creating test files. run_dir: %s, workflow type: %s', run_dir, workflow_type)

        try:
            # get the test executor run location
            executor = next(iter(run_data['request_data']['tests']))

            # is this a legit executor?
            if executor in StagingTestExecutor.__members__:
                # get the list of tests for this executor
                tests = run_data['request_data']['tests'][executor]

                # check the list of tests
                if len(tests) > 0:
                    # generate the output path/file name
                    out_file_name = os.path.join(run_dir, f'{executor}_test_list.sh')

                    # write out the data
                    with open(out_file_name, 'w', encoding='utf-8') as fp:
                        self.logger.debug('Writing to %s', out_file_name)

                        # write out the preamble and get into the test results directory
                        fp.write('#/bin/bash\ncd /var/lib/irods;\n')

                        # init the base command line.
                        base_cmd_line: str = ''

                        # init the topology test type
                        topology_test_type: str = ''

                        # get the data path
                        data_path: str = os.path.join(run_dir, executor)

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

                        # create the results directory in the k8s file store
                        fp.write(f'echo "Creating the run results dir {data_path}..."; mkdir {data_path};\n')

                        # save the log directory for extended forensics
                        fp.write(f'echo "Copying /var/lib/irods/log dir into {data_path}..."; cp -R /var/lib/irods/log {data_path};\n')

                        # save the log directory for extended forensics
                        fp.write(f'echo "Copying /var/lib/irods/test-reports dir into {data_path}..."; cp -R /var/lib/irods/test-reports'
                                 f' {data_path};\n')

                        # this directory may or may not exist
                        fp.write(f'echo "Copying /var/log/irods dir into {data_path}..."; cp -R /var/log/irods {data_path};\n')

                    # make sure the file has the correct permissions
                    if sys.platform != 'win32':
                        os.chmod(out_file_name, 0o777)

                else:
                    self.logger.debug('WARNING: An executor was specified with no tests. executor name %s, run_dir: %s, workflow type: %s', executor,
                                      run_dir, workflow_type.name)
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

    def final_staging(self, run_id: str, run_dir: str, staging_type: StagingType) -> ReturnCodes:
        """
        Performs the final staging

        :param run_id: The ID of the supervisor run request.
        :param run_dir: The path of the directory to use for the staging operations.
        :param staging_type: The type of staging step, either 'initial' or 'final'
        :return:
        """
        # init the return code
        ret_val: ReturnCodes = ReturnCodes.EXIT_CODE_SUCCESS

        # create the full run directory name
        new_run_dir = os.path.join(run_dir, run_id)

        self.logger.info('Final staging version %s start: run_dir: %s', self.app_version, new_run_dir)

        try:
            # does the directory exist?
            if os.path.isdir(new_run_dir):
                self.logger.info('Run dir exists. run_dir: %s', new_run_dir)

                # try to make the call for run data records
                run_data: json = self.db_info.get_run_def(run_id)

                # did getting the data to go ok
                if run_data != ReturnCodes.DB_ERROR:
                    # make the call to get the run status
                    run_status = self.db_info.get_run_status(run_data['request_group'])

                    # if all runs are complete
                    if run_status['Testing Jobs']['Total'] == run_status['Testing Jobs']['Complete']:
                        # get the full path to the test results archive file
                        k8s_archive_file: str = os.path.join(run_dir, f"{run_data['request_group']}.test-results")

                        self.logger.info('Creating k8s archive: %s.zip', k8s_archive_file)

                        # compress the directory into the k8s data directory
                        shutil.make_archive(k8s_archive_file, 'zip', run_dir)

                        # if the package directory is defined
                        if run_data['request_data']['package-dir']:
                            # get the full path to the test results archive file
                            nfs_archive_file: str = os.path.join(run_data['request_data']['package-dir'], f"{run_data['request_group']}.test-results")

                            self.logger.info('Creating nfs archive: %s.zip', k8s_archive_file)

                            # compress the directory into the package directory
                            shutil.make_archive(nfs_archive_file, 'zip', run_dir)

                            # adjust the file properties of the archive to 775
                            os.chmod(f'{nfs_archive_file}.zip', 0o775)

                        # remove all directories from the run (leaving the archive file)
                        [shutil.rmtree(data_dir, ignore_errors=True) for data_dir in glob.glob(f'{run_dir}/**/')]
            else:
                ret_val = ReturnCodes.ERROR_NO_RUN_DIR
        except Exception:
            # declare ready
            self.logger.exception('Exception: The iRODS K8s "%s" final staging request for run directory %s failed.', staging_type, new_run_dir)

            # set the exception error code
            ret_val = ReturnCodes.EXCEPTION_RUN_PROCESSING

        self.logger.info('Final staging complete: run_dir: %s, ret_val: %s', new_run_dir, ret_val)

        # return the result to the caller
        return ret_val
