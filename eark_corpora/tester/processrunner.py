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
import json
import time
from typing import List, Tuple
import subprocess

class ProcessResult:
    """Package result class."""
    def __init__(self, retcode: int, stdout: str, stderr: str, duration:float, exception: Exception = None):
        self.retcode: int = retcode
        self.stdout: str = stdout
        self.stderr: str = stderr
        self.duration: float = duration
        self.exception: Exception = exception

    def __repr__(self):
        return f"PackageResult(package_name={self.package_name}, test_case_id={self.test_case_id}, retcode={self.retcode})"

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__).replace('\\n', '').replace('\\"', '"').replace('"{', '{').replace('}"', '}')

def run_process(command: List[str]) -> ProcessResult:
    start = time.time()
    try:
        proc_results = subprocess.run(command, capture_output=True, timeout=60, text=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        return ProcessResult(e.returncode, e.stdout.decode('utf-8').strip(), e.stderr.decode('utf-8').strip(), time.time() - start, exception=e)
    return ProcessResult(proc_results.returncode, proc_results.stdout, proc_results.stderr, time.time() - start)
