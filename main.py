# BSD 3-Clause All rights reserved.
#
# SPDX-License-Identifier: BSD 3-Clause

"""
    Main entry point for the staging microservice application

"""
import sys
from argparse import ArgumentParser
from src.staging.staging import Staging
from src.common.staging_enums import StagingType, WorkflowTypeName

if __name__ == '__main__':
    # Main entry point for the staging microservice
    #
    # Args expected:
    #    --run_id - The ID of the supervisor run request.
    #    --type - The type of staging step, either 'initial' or 'final'
    #    --run_dir - The name of the target directory to use for operations

    # create a staging object
    stage_obj = Staging()

    # create a command line parser
    parser = ArgumentParser()

    # declare the command params
    parser.add_argument('--run_id', default=None, help='The run identifier.', type=str, required=True)
    parser.add_argument('--run_dir', default=None, help='The name of the run directory to use for the staging operations.', type=str, required=True)
    parser.add_argument('--step_type', default=None, help='The type of staging step, initial or final.', type=str, required=True)
    parser.add_argument('--workflow_type', default='CORE', help='The type of workflow, CORE, TOPOLOGY, etc..', type=str, required=False)

    # collect the params
    args = parser.parse_args()

    # init the return value
    ret_val: int = 0

    # validate the inputs
    if args.run_id != '' and args.run_id != '' and args.step_type != '' and args.workflow_type != '':
        try:
            # check to make sure we got a legit staging and workflow types
            # these will throw exceptions if they are not
            tmp = StagingType(args.step_type)
            tmp2 = WorkflowTypeName(args.workflow_type)
        except Exception:
            # invalid input types
            ret_val: int = -2
    else:
        # missing 1 or more params
        ret_val: int = -3

    # should we continue?
    if ret_val == 0:
        # do the staging
        ret_val = stage_obj.run(args.run_id, args.run_dir, args.step_type, args.workflow_type)

    # exit with the final exit code
    sys.exit(ret_val)
