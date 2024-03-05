# BSD 3-Clause License All rights reserved.
#
# SPDX-License-Identifier: BSD 3-Clause License

"""
    Class enums for the project

    Author: Phil Owen, RENCI.org
"""

from enum import Enum


class StagingType(str, Enum):
    """
    Class enums to represent the staging states

    """
    # initial staging
    INITIAL_STAGING = 'initial'

    # final staging
    FINAL_STAGING = 'final'


class WorkflowTypeName(str, Enum):
    """
    Class enums for the supervisor workflow names
    """
    CORE = 'CORE'
    FEDERATION = 'FEDERATION'
    PLUGIN = 'PLUGIN'
    TOPOLOGY = 'TOPOLOGY'
    UNIT = 'UNIT'


class StagingTestExecutor(str, Enum):
    """
    Class enums to specify the different test executor types

    """
    # consumer tests
    CONSUMER = 'consumer'
    CONSUMERSECONDARY = 'consumersecondary'
    CONSUMERTERTIARY = 'consumertertiary'

    # provider tests
    PROVIDER = 'provider'
    PROVIDERSECONDARY = 'providersecondary'


class ReturnCodes(int, Enum):
    """
    Class enum for error codes
    """
    EXIT_CODE_SUCCESS = 0
    DB_ERROR = -1
    EXCEPTION_RUN_PROCESSING = -99
    ERROR_TEST_FILE = -98
    ERROR_NO_RUN_DIR = -97
