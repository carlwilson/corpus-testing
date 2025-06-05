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
        Command line corpora reporting tool
"""
import shutil
import sys
import importlib.metadata
import argparse
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, Template

from eark_validator.specifications.specification import SpecificationType

from eark_corpora.model.corpora import Corpus, CorpusTestCase
from eark_corpora.loader import get_corpora, corpus_root

__version__ = importlib.metadata.version('eark_corpora')
environment: Environment = Environment(loader=FileSystemLoader('templates/'))
reports_root = Path('./site')
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
PARSER = argparse.ArgumentParser(prog='eark-corpora',
                                 description=defaults['description'],
                                 epilog=defaults['epilog'])

def parse_command_line():
    """Parse command line arguments."""
    PARSER.add_argument('--version',
                        action='version',
                        version=__version__)
    # Parse arguments
    args = PARSER.parse_args()
    return args

def _iterate_corpora(corpora: dict[SpecificationType, Corpus] = None):
    """Iterate over all specifications."""
    # Render the home overview report
    _render_template(reports_root, 'home.html.jinja', { 'corpora': corpora.values() })
    # iterate over each corpus and output the reports
    for corpus in corpora.values():
        _output_corpus(corpus)

def _output_corpus(corpus: Corpus):
    # Render the top level corpus report
    _render_template(reports_root / corpus.specification.id, 'corpus.html.jinja', _get_corpus_context(corpus))
    # Render the test cases
    _output_cases(corpus)

def _output_cases(corpus: Corpus):
    # Iterate the corpus test cases and output the test case reports
    for test_case in corpus.test_cases:
        _render_template(reports_root / corpus.specification.id / test_case.id,
            'case.html.jinja',
            {
               'test_case': test_case,
                'corpus': corpus
            }
        )
        # Now output the packages for each test case
        _output_packages(test_case, corpus)

def _output_packages(test_case: CorpusTestCase, corpus: Corpus):
    """Output packages for a test case."""
    for rule in test_case.rules:
        for package in rule.packages:
            _render_template(reports_root / corpus.specification.id / test_case.id / package.name,
                'package.html.jinja',
                {
                    'package': package,
                    'case': test_case,
                    'rule': rule,
                    'corpus': corpus,
                }
            )



def _get_corpus_context(corpus: Corpus) -> dict:
    """Get the corpus context."""
    spec_requirements: set[str] = _get_specification_requirements(corpus)
    corpus_requirements: set[str] = _get_corpus_requirements(corpus)
    return {
        'corpus': corpus,
        'missing_corpus': spec_requirements.difference(corpus_requirements),
        'missing_spec': corpus_requirements.difference(spec_requirements),
    }

def _get_specification_requirements(corpus: Corpus) -> set[str]:
    spec_requirements: set[str] = set()
    # Populate the specification requirements set
    for requirements in corpus.specification.requirements.values():
        for requirement in requirements:
            assert requirement.id not in spec_requirements, f"Duplicate requirement ID: {requirement.id}"
            spec_requirements.add(requirement.id)
    for requirement in corpus.specification.structural_requirements:
        assert requirement.id not in spec_requirements, f"Duplicate requirement ID: {requirement.id}"
        spec_requirements.add(requirement.id)
    return spec_requirements

def _get_corpus_requirements(corpus: Corpus) -> set[str]:
    corpus_dir: Path = corpus_root / corpus.specification.id
    corpus_requirements: set[str] = set()
    for filename in corpus_dir.iterdir():
        if filename.is_dir() and filename.name.startswith(corpus.specification.id):
            corpus_requirements.add(filename.name)
    return corpus_requirements

def _setup():
    # If the reports root exists, clear out the old reports
    if reports_root.exists():
        for filename in reports_root.iterdir():
            # Remove index.html files and directories that are not 'static'
            if filename.is_file() and filename.name == 'index.html':
                filename.unlink()
            elif filename.is_dir() and filename.name != 'static':
                shutil.rmtree(filename)
    else:
        # Create the reports root directory if it does not exist
        reports_root.mkdir(parents=True, exist_ok=True)

def _render_template(output_dir: Path, template_name: str, context: dict, output_file: str = 'index.html'):
    # Make sure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    # load the template and render it with the context
    template: Template = environment.get_template(template_name)
    with open(output_dir / output_file, 'w', encoding='utf-8') as f:
        f.write(template.render(context))

def main():
    """Main command line application."""
    _exit: int = 0
    # Get input from command line
    _ = parse_command_line()
    # Set up the reports root directory
    _setup()
    # Iterate over the corpora and output the reports
    _iterate_corpora(get_corpora())
    sys.exit(_exit)

# def _test_case_schema_checks():
if __name__ == '__main__':
    main()
