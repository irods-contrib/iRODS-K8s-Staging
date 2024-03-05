<!--
BSD 3-Clause License All rights reserved.

SPDX-License-Identifier: BSD 3-Clause License
-->

[![iRODS](iRODS-Logo.png)](https://docs.irods.org)

# iRODS-K8s Staging
The iRODS-K8s Staging workflow step microservice.

#### Licenses...
[![MIT License](https://img.shields.io/badge/License-MIT-orange.svg)](https://github.com/irods-contrib/iRODS-K8s-Staging/blob/main/LICENSE)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![RENCI License](https://img.shields.io/badge/License-RENCI-blue.svg)](https://www.renci.org/)
#### Components and versions...
[![Python](https://img.shields.io/badge/Python-3.12.2-orange)](https://github.com/python/cpython)
[![Linting Pylint](https://img.shields.io/badge/Pylint-%203.1.0-yellow)](https://github.com/PyCQA/pylint)
[![Pytest](https://img.shields.io/badge/Pytest-%208.0.2-blue)](https://github.com/pytest-dev/pytest)
#### Build status...
[![PyLint the codebase](https://github.com/irods-contrib/iRODS-K8s-Staging/actions/workflows/pylint.yml/badge.svg)](https://github.com/irods-contrib/iRODS-K8s-Staging/actions/workflows/pylint.yml)
[![Build and push the Docker image](https://github.com/irods-contrib/iRODS-K8s-Staging/actions/workflows/image-push.yml/badge.svg)](https://github.com/irods-contrib/iRODS-K8s-Staging/actions/workflows/image-push.yml)

## Description
The iRODS-K8s Staging product is a microservice used in the iRODS K8s Supervisor workflow step to:
 - Perform data initializations and create configuration files for standup and testing.
 - Performs finalization operations when the workflow is complete.

There are GitHub actions to maintain code quality in this repo:
 - Pylint (minimum score of 10/10 to pass),
 - Build/publish a Docker image.
