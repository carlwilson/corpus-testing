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
"""
E-ARK : Corpus Reporting
"""
from functools import lru_cache
from pathlib import Path

from eark_validator.specifications.specification import EarkSpecification, SpecificationType, SpecificationVersion
from eark_corpora.model.corpora import Corpus
from eark_corpora.cli.config import AppConfig


corpus_root = Path('./eark-ip-test-corpus/corpus')

@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Get the application configuration."""
    return AppConfig()

@lru_cache(maxsize=1)
def get_corpora() -> dict[SpecificationType, Corpus]:
    corpora: dict[SpecificationType, Corpus] = {}
    for spec_type in SpecificationType:
        specification = EarkSpecification(spec_type, SpecificationVersion.V2_1_0).specification
        corpora[spec_type] = Corpus.from_directory(specification, corpus_root / specification.id)
    return corpora
