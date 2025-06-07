#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
"""
E-ARK : Corpora Reporting
        Command line corpora testing tool
"""
import shutil
import sys
import importlib.metadata
import argparse
from pathlib import Path
from typing import Dict, List

from eark_validator.specifications.specification import SpecificationType

from eark_corpora.loader import get_corpora, corpus_root
from eark_corpora.model.corpora import Corpus
from eark_corpora.model.runners import ProcessResult
from eark_corpora.tester.processrunner import run_process
from eark_corpora.tester.utils import get_runners

__version__ = importlib.metadata.version('eark_corpora')
results_root = Path('./results')
defaults = {
    'description': """E-ARK Corpusra Reporting Tool
is a command-line tool to test validators against the E-ARK corpus.""",
    'epilog': """
DILCIS Board (http://dilcis.eu)
See LICENSE for license information.
GitHub: https://github.com/DILCISBoard/corpus-testing
Author: Carl Wilson (OPF), 2025
Maintainer: Carl Wilson (OPF), 2025"""
}

# Create PARSER
PARSER = argparse.ArgumentParser(prog='eark-tester',
                                 description=defaults['description'],
                                 epilog=defaults['epilog'])

def parse_command_line():
    """Parse command line arguments."""
    PARSER.add_argument('--version',
                        action='version',
                        version=__version__)
    PARSER.add_argument('--clear',
                        action='store_true',
                        dest='clear',
                        default=False,
                        help='Clear the results directory before running tests.')
    # Parse arguments
    args = PARSER.parse_args()
    return args

def _setup():
    if results_root.exists():
        for filename in results_root.iterdir():
            if filename.is_file() or filename.is_symlink():
                filename.unlink()
            elif filename.is_dir():
                shutil.rmtree(filename)
    else:
        results_root.mkdir(parents=True, exist_ok=True)

def test_runners():
    """Test the runners."""
    corpora: Dict[SpecificationType, Corpus] = get_corpora()
    for corpus in corpora.values():
        for test_case in corpus.test_cases:
            for rule in test_case.rules:
                for package in rule.packages:
                    if not package.has_directory or not package.path or package.path.name == '':
                        continue
                    relative_path = Path(corpus.specification.id) / str(test_case.id) / package.path
                    package_path = corpus_root / relative_path
                    results: Dict[str, ProcessResult] = validate_package(package_path)

                    for result_id, result in results.items():
                        output_path: Path = results_root / relative_path
                        output_path.mkdir(parents=True, exist_ok=True)
                        with open(output_path / (result_id + '.json'), 'w') as f:
                            f.write(result.toJson())
                        if result.retcode != 0:
                            print(f"Error running { result.runner_details.name } for package {package.name} for test case {test_case.id}")
                        else:
                            print(f"Successfully ran { result.runner_details.name } for package {package.name} for test case {test_case.id}")

def validate_package(package_path: Path) -> Dict[str, ProcessResult]:
    results: Dict[str, ProcessResult] = {}
    for runner_id, runner in get_runners().items():
        command: List[str] = runner.commands.get('pre', []).copy()
        command.append(package_path)
        command+= runner.commands.get('post', [])
        result: ProcessResult = run_process(runner.details, command)
        if (runner_id == 'commons-ip') and (result.retcode == 0):
            file_name = Path(result.stdout[result.stdout.find("'")+1:-1])
            with open(file_name, 'r', encoding='utf-8') as _f:
                contents: str = _f.read()
                result.stdout = contents
            file_name.unlink()
        elif (result.retcode == 0):
            output = result.stdout[result.stdout.find("{"):]
            result.stdout = output

        results[runner_id + runner.details.version] = result
    return results

def main():
    """Main command line application."""
    _exit: int = 0
    # Get input from command line
    args = parse_command_line()
    if args.clear:
        _setup()
    test_runners()
    sys.exit(_exit)

# def _test_case_schema_checks():
if __name__ == '__main__':
    main()
