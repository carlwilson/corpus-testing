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

from functools import lru_cache
import json
from eark_corpora.loader import get_config
from eark_corpora.model.runners import Runner
from eark_corpora.tester.processrunner import ProcessResult, run_process

@lru_cache(maxsize=1)
def get_runners() -> dict[str, Runner]:
    runners: dict[str, Runner] = {}
    with open(get_config().testing_config, 'r') as f:
        data = json.load(f)
        if not isinstance(data, dict) or 'runners' not in data:
            raise ValueError("Invalid testing configuration file format.")
        for runner_dict in data['runners']:
            if not isinstance(runner_dict, dict) or 'commands' not in runner_dict:
                raise ValueError("Invalid runner configuration format.")
            version = get_version(runner_dict)
            runner_dict.update({'version': version})
            runner = Runner(**runner_dict)
            runners[runner.id] = runner
    return runners

def get_version(runner_dict: dict) -> str:
    """Get the version of a specific runner."""
    commands = runner_dict.get('commands', {})
    if not isinstance(commands, dict) or 'version' not in commands:
        raise ValueError("Invalid commands format in runner configuration.")
    result: ProcessResult = run_process(commands['version'])
    if result.retcode != 0:
        raise RuntimeError(f"Error running version command: {result.stderr.decode('utf-8')}")
    return result.stdout.strip().split(' ')[-1]  # Assuming version is the first part of the output