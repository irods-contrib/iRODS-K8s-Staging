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

from src.common.logger import LoggingUtil
from src.common.pg_impl import PGImplementation
from src.common.staging_enums import StagingType


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
        self.logger = LoggingUtil.init_logging("iRODS.K8s.Staging", level=log_level, line_format='medium', log_file_path=log_path)

        # specify the DB to get a connection
        # note the extra comma makes this single item a singleton tuple
        db_names: tuple = ('irods-sv',)

        # create a DB connection object
        self.db_info: PGImplementation = PGImplementation(db_names, _logger=self.logger)

    def run(self, run_dir: str, step_type: StagingType) -> int:
        """
        Performs the requested type of staging operation.

        The supervisor will mount the /data directory for this component by default.

        :param run_dir: The base path of the directory to use for the staging operations.
        :param step_type: The type of staging step, either 'initial' or 'final'

        :return:
        """
        # init the return value
        ret_val: int = 0

        # is this an initial stage step
        if step_type == StagingType.INITIAL_STAGING:
            # get the run ID
            run_id: str = run_dir.split('/')[-1]

            # make the call to perform the op
            ret_val = self.initial_staging(run_dir, run_id, step_type)
        # else this a final stage step
        elif step_type == StagingType.FINAL_STAGING:
            # make the call to perform the op
            ret_val = self.final_staging(run_dir, step_type)

        # return to the caller
        return ret_val

    def initial_staging(self, run_dir: str, run_id: str, staging_type: StagingType) -> int:
        """
        Performs the initial staging

        :param run_dir: The path of the directory to use for the staging operations.
        :param run_id: The ID of the supervisor run request.
        :param staging_type: The type of staging step, either 'initial' or 'final'
        :return:
        """
        # init the return code
        ret_val: int = 0

        try:
            # try to make the call for records
            run_data: json = self.db_info.get_run_def(run_id)

            # did getting the data go ok
            if run_data != -1:
                # make the directory
                os.makedirs(run_dir, exist_ok=True)

                # create the file that contains the test list
                with open(os.path.join(run_dir, 'test_list.json'), 'w', encoding='utf-8') as fp:
                    fp.write(json.dumps(run_data['request_data']['tests']))
            else:
                # set the return value
                ret_val = run_data

        except Exception:
            # declare ready
            self.logger.exception('Exception: The iRODS K8s "%s" staging request for run directory %s failed.', staging_type, run_dir)

            # set the exception error code
            ret_val = -99

        # return the result to the caller
        return ret_val

    def final_staging(self, run_dir: str, staging_type: StagingType) -> int:
        """
        Performs the initial staging

        :param run_dir: The path of the directory to use for the staging operations.
        :param staging_type: The type of staging step, either 'initial' or 'final'
        :return:
        """
        # init the return code
        ret_val: int = 0

        try:
            # remove the run directory
            shutil.rmtree(run_dir)

        except Exception:
            # declare ready
            self.logger.exception('Exception: The iRODS K8s "%s" staging request for run directory %s failed.', staging_type, run_dir)

            # set the exception error code
            ret_val = -99

        # return the result to the caller
        return ret_val
