#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# E-ARK Corpus Reporting
# Copyright (C) 2025
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
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel

class RunnerDetails(BaseModel):
    """Details of a runner."""
    id: str   # Unique identifier for the runner
    name: str # Name of the runner
    version: str # Version of the runner
    URL: str # URL for the runner documentation or homepage

class Runner(BaseModel):
    """Package class for testing purposes."""
    details: RunnerDetails
    commands: Dict[str, List[str]] = {}

class ProcessResult:
    """Package result class."""
    def __init__(self, runner_details: RunnerDetails, retcode: int, stdout: str, stderr: str, duration:float, exception: Exception = None, timestamp: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
        self.runner_details: RunnerDetails = runner_details
        self.timestamp: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.retcode: int = retcode
        self.stdout: str = stdout
        self.stderr: str = stderr
        self.duration: float = duration
        self.exception: Exception = exception

    def __repr__(self):
        return f"PackageResult(package_name={self.package_name}, test_case_id={self.test_case_id}, retcode={self.retcode})"

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__).replace('\\n', '').replace('\\"', '"').replace('\\\\"', "'").replace('"{', '{').replace('}"', '}')
    
    @classmethod
    def from_file(cls, file_path: Path):
        """Load ProcessResult from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                runner_details: RunnerDetails = RunnerDetails(**data['runner_details'])
                data['runner_details'] = runner_details
                return cls(**data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading ProcessResult from {file_path}: {e}")
            raise ValueError(f"Invalid ProcessResult file: {file_path}") from e
