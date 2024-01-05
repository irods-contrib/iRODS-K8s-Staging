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

from src.staging.staging import Staging

if __name__ == '__main__':
    """
    Main entry point

    Args expected:
        --run_id - The ID of the supervisor run request.
        --type - The type of staging step, either 'initial' or 'final'
        --run_dir - The name of the target directory to use for operations
    """
    from argparse import ArgumentParser

    stage_obj = Staging()

    parser = ArgumentParser()
    parser.add_argument('--run_id', default=None, help='The Supervisor run request ID.', type=str, required=True)
    parser.add_argument('--step_type', default=None, help='The type of staging step, initial or final.', type=str, required=True)
    parser.add_argument('--run_dir', default=None, help='The name of the run directory to use for the staging operations.', type=str, required=True)

    args = parser.parse_args()

    # init the return
    result = 0

    # validate the inputs
    if args.run_id != '' and args.run_dir != '' and args.step_type != '':
        # check to make sure we got a legit staging type
        if args.step_type not in ['initial', 'final']:
            # set an error code
            result = -2
    else:
        # missing 1 or more params
        result = -3

    # should we continue
    if result == 0:
        # do the staging
        result = stage_obj.run(args.run_id, args.run_dir, args.step_type)

    # exit with the final exit code
    exit(result)
