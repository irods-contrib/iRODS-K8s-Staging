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
from src.common.logger import LoggingUtil
from src.common.pg_impl import PGImplementation


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

    def run(self, run_id: str, run_dir: str, step_type: str) -> int:
        """
        Performs the requested type of staging operation.

        The supervisor will mount the /data directory for this component.

        :param run_id: The ID of the supervisor run request.
        :param run_dir: The base path of the directory to use for the staging operations.
        :param step_type: The type of staging step, either 'initial' or 'final'

        :return:
        """
        # init the return value
        ret_val: int = 0

        try:
            # get the full path to the target directory
            full_path = os.path.join(run_dir, run_id)

            # make the directory
            os.makedirs(full_path, exist_ok=True)

            # try to make the call for records
            run_data = self.db_info.get_run_def(run_id)

            # was there an error getting the data
            if run_data == -1:
                # set the return value
                ret_val = run_data
            # go ahead and process the request
            else:
                # is this a initial stage step
                if step_type == 'initial':
                    # create the file that contains the test list
                    with open(os.path.join(full_path, 'test_list.json'), 'w', encoding='utf-8') as fp:
                        fp.write(json.dumps(run_data['request_data']['tests']))

                # is this a final stage step
                elif step_type == 'final':
                    pass

        except Exception:
            # declare ready
            self.logger.exception('Exception: The iRODS K8s Staging "%s" request for run id %s failed.', step_type, run_id)

            ret_val = -99

        # return to the caller
        return ret_val
