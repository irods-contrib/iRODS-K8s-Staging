<!--
SPDX-FileCopyrightText: 2022 Renaissance Computing Institute. All rights reserved.
SPDX-FileCopyrightText: 2023 Renaissance Computing Institute. All rights reserved.
SPDX-FileCopyrightText: 2024 Renaissance Computing Institute. All rights reserved.

SPDX-License-Identifier: GPL-3.0-or-later
SPDX-License-Identifier: LicenseRef-RENCI
SPDX-License-Identifier: MIT
-->

![image not found](renci-logo.png "RENCI")

# iRODS-K8s Staging
The iRODS-K8s Staging workflow step microservice.

#### Licenses...
[![MIT License](https://img.shields.io/badge/License-MIT-orange.svg)](https://github.com/irods-contrib/iRODS-K8s-Staging/blob/main/LICENSE)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![RENCI License](https://img.shields.io/badge/License-RENCI-blue.svg)](https://www.renci.org/)
#### Components and versions...
[![Python](https://img.shields.io/badge/Python-3.11.7-orange)](https://github.com/python/cpython)
[![Linting Pylint](https://img.shields.io/badge/Pylint-%203.0.3-yellow)](https://github.com/PyCQA/pylint)
[![Pytest](https://img.shields.io/badge/Pytest-%207.4.4-blue)](https://github.com/pytest-dev/pytest)
#### Build status...
[![PyLint the codebase](https://github.com/irods-contrib/iRODS-K8s-Staging/actions/workflows/pylint.yml/badge.svg)](https://github.com/irods-contrib/iRODS-K8s-Staging/actions/workflows/pylint.yml)
[![Build and push the Docker image](https://github.com/irods-contrib/iRODS-K8s-Staging/actions/workflows/image-push.yml/badge.svg)](https://github.com/irods-contrib/iRODS-K8s-Staging/actions/workflows/image-push.yml)

## Description
The iRODS-K8s Staging product is a microservice used in a iRODS K8s Supervisor workflow step to:
 - Perform data initializations and create configuration files for standup and testing.
 - Performs finalization operations when the workflow is complete.

There are GitHub actions to maintain code quality in this repo:
 - Pylint (minimum score of 10/10 to pass),
 - Build/publish a Docker image.
