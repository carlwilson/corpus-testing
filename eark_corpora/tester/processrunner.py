#!/usr/bin/env python
# coding=UTF-8
#
# E-ARK Validation
# Copyright (C) 2019
# All rights reserved.
#
# Licensed to the E-ARK project under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The E-ARK project licenses
# this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#
import time
from typing import List
import subprocess

from eark_corpora.model.runners import ProcessResult, RunnerDetails

def run_process(runner_details: RunnerDetails, command: List[str]) -> ProcessResult:
    start = time.time()
    try:
        proc_results = subprocess.run(command, capture_output=True, timeout=60, text=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return ProcessResult(e.returncode,
                             e.stdout.strip(),
                             e.stderr.strip().replace('"', "'"),
                             time.time() - start,
                             exception=e)
    return ProcessResult(runner_details,
                         proc_results.returncode,
                         proc_results.stdout.strip(),
                         proc_results.stderr.strip().replace('"', "'"),
                         time.time() - start)
