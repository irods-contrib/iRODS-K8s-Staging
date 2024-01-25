# SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
# SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.
#
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-License-Identifier: LicenseRef-RENCI
# SPDX-License-Identifier: MIT

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
