# BSD 3-Clause All rights reserved.
#
# SPDX-License-Identifier: BSD 3-Clause

"""
    Class for database functionalities

    Author: Phil Owen, RENCI.org
"""
from src.common.pg_utils_multi import PGUtilsMultiConnect
from src.common.logger import LoggingUtil


class PGImplementation(PGUtilsMultiConnect):
    """
        Class that contains DB calls for the job supervisor.

        Note this class inherits from the PGUtilsMultiConnect class
        which has all the connection and cursor handling.
    """

    def __init__(self, db_names: tuple, _logger=None, _auto_commit=True):
        # if a reference to a logger passed in use it
        if _logger is not None:
            # get a handle to a logger
            self.logger = _logger
        else:
            # get the log level and directory from the environment.
            log_level, log_path = LoggingUtil.prep_for_logging()

            # create a logger
            self.logger = LoggingUtil.init_logging("iRODS.Supervisor.Jobs.PGImplementation", level=log_level, line_format='medium',
                                                   log_file_path=log_path)

        # init the base class
        PGUtilsMultiConnect.__init__(self, 'iRODS.Supervisor.Jobs.PGImplementation', db_names, _logger=self.logger, _auto_commit=_auto_commit)

    def __del__(self):
        """
        Calls super base class to clean up DB connections and cursors.

        :return:
        """
        # clean up connections and cursors
        PGUtilsMultiConnect.__del__(self)

    def get_run_def(self, run_id: str):
        """
        gets the supervisor run request for the run id passed.

        :return:
        """

        # create the sql
        sql: str =  f'SELECT public.get_supervisor_run_def_json({run_id})'

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val

    def get_run_status(self, request_group):
        """
        gets the run status

        :return:
        """

        # create the sql
        sql: str = f"SELECT public.get_run_status_json('{request_group}');"

        # get the data
        ret_val = self.exec_sql('irods-sv', sql)

        # return the data
        return ret_val