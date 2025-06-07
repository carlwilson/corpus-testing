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
from enum import Enum, unique
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from lxml import etree
from xsdata.formats.dataclass.parsers import XmlParser
from pydantic import BaseModel, computed_field

from eark_validator.model.specifications import Specification
from eark_validator.specifications.specification import SpecificationType, SpecificationVersion

from eark_corpora.model.casexml import TestCase, Rule, Package
from eark_corpora.model.runners import ProcessResult, RunnerDetails


@unique
class Testable(str, Enum):
    """Enumeration for testable states."""
    """Defines the possible states of a testable item."""
    # The states are represented as strings for easier serialization and comparison.
    FALSE = "FALSE"
    TRUE = "TRUE"
    UNKNOWN = "UNKNOWN"
    PARTIAL = "PARTIAL"

    @classmethod
    def from_str(cls, value: str) -> 'Testable':
        """Convert a string to a Testable enum."""
        if value.upper() in cls._value2member_map_:
            return cls(value.upper())
        return cls.UNKNOWN

@unique
class Level(str, Enum):
    ERROR = "ERROR"
    INFO = "INFO"
    WARNING = "WARN"

    @classmethod
    def from_str(cls, value: str) -> 'Level':
        """Convert a string to a Level enum."""
        if value.upper() in cls._value2member_map_:
            return cls(value.upper())
        return cls.ERROR

class TestCaseId(BaseModel):
    """TestCaseId class for testing purposes."""
    id: str
    version: SpecificationVersion
    type: SpecificationType

class CorpusTestResult(BaseModel):
    """CorpusTestResult class for testing
    purposes."""
    details: RunnerDetails
    requirement_id: str
    ret_code: int = -1
    duration: float = 0.0
    struct_status: str = 'Unknown'
    schema_status: str = 'Unknown'
    schematron_status: str = 'Unknown'
    error_ids: Dict[str, Level] = {}
    error_msg: str = ''

    @property
    def is_valid(self) -> bool:
        """Check if the test result is valid."""
        return self.ret_code == 0 and self.struct_status == 'WellFormed' and self.schema_status == 'Valid' and self.schematron_status == 'Valid'
    
    @property
    def contains_code(self) -> bool:
        """Check if the test result contains code."""
        return self.requirement_id in self.error_ids.keys()
    
    @classmethod
    def from_process_result(cls, process_result: ProcessResult, test_case_id: str) -> 'CorpusTestResult':
        """Create a CorpusTestResult from a ProcessResult."""
        if process_result.retcode != 0 or not isinstance(process_result.stdout, dict):
            error_msg = str(process_result.stderr) if process_result.stderr else process_result.stdout
            return CorpusTestResult(
                details=process_result.runner_details,
                requirement_id=test_case_id,
                ret_code=process_result.retcode,
                error_msg=error_msg,
                duration=process_result.duration, 
            )
        error_ids: Dict[str, Level] = {}
        struct_status, ids = cls._get_results(process_result.stdout.get('structuralResults', {}))
        error_ids.update(ids)
        schema_status = 'Unknown'
        schematron_status = 'Unknown'
        metadata = process_result.stdout.get('metadata', {})
        if metadata:
            schema_name = 'schemaResults' if process_result.runner_details.id == 'commons-ip' else 'schema_results'
            schema_status, ids = cls._get_results(metadata.get(schema_name, {}), process_result.runner_details.id == 'commons-ip')
            error_ids.update(ids)
            schematron_name = 'schematronResults' if process_result.runner_details.id == 'commons-ip' else 'schematron_results'
            schematron_status, ids = cls._get_results(metadata.get(schematron_name, {}), process_result.runner_details.id == 'commons-ip')
            error_ids.update(ids)
        return CorpusTestResult(
            details=process_result.runner_details,
            requirement_id=test_case_id,
            ret_code=process_result.retcode,
            struct_status=struct_status,
            schema_status=schema_status,
            schematron_status=schematron_status,
            duration=process_result.duration,
            error_ids=error_ids,
        )
    
    @classmethod
    def _get_results(cls, result_dict: Dict, is_commons_ip: bool = False) -> Tuple[str, Dict[str, Level]]:
        error_ids: Dict[str, Level] = {}
        status: str = 'Unknown'
        status_name: str = 'status' if is_commons_ip else 'level'
        rule_name: str = 'ruleId' if is_commons_ip else 'rule_id'
        if result_dict:
            status = result_dict.get(status_name, 'Unknown')
            for message in result_dict.get('messages', []):
                error_ids.update({ message.get(rule_name, 'Unknown') : Level.from_str(message.get('level', 'ERROR')) })
        return status, error_ids


class CorpusPackage(BaseModel):
    """Package class for testing purposes."""
    name: str
    description: str
    path: Path
    is_implemented: bool
    is_valid: bool
    has_directory: bool
    has_mets: bool
    test_results: List[CorpusTestResult] = []

class CorpusRule(BaseModel):
    """Rule class for testing purposes."""
    id: int
    description: str
    level: Level
    message: Optional[str] = None
    packages: list[CorpusPackage]

    @classmethod
    def from_rule(cls, rule: Rule, root: Path) -> 'CorpusRule':
        """Create a CorpusRule from a Rule."""
        return cls(
            id=rule.id,
            description=rule.description.value,
            level=Level.from_str(rule.error.level.value),
            message=rule.error.message.value if rule.error is not None else None,
            packages=[CorpusPackage(
                name=package.name,
                description=package.description.value,
                path=Path(package.path.value),
                is_implemented=package.is_implemented.value == "TRUE",
                is_valid=package.is_valid.value == "TRUE",
                has_directory = cls._has_directory(package, root),
                has_mets = cls._has_mets(package, root) 
            ) for package in rule.corpus_packages.package],
        )

    @classmethod
    def _has_directory(cls, package: Package, root: Path) -> bool:
        """Check if the package is implemented and valid."""
        return (root / Path(package.path.value)).is_dir()

    @classmethod
    def _has_mets(cls, package: Package, root: Path) -> bool:
        """Check if the package is implemented and valid."""
        return (root / Path(package.path.value) / 'METS.xml').is_file()

    @property
    def implemented_packages(self) -> list[str]:
        """Get the implemented packages."""
        return [package.name for package in self.packages if package.is_implemented]

class CorpusTestCase(BaseModel):
    id: str
    description: Optional[str]
    is_xml_valid: bool
    xml_validation_error: Optional[str]
    testable: Testable
    rules : list[CorpusRule]
    """TestCase class for testing purposes."""

    @property
    def packages(self) -> list[CorpusPackage]:
        """Get the rules from the specification."""
        packages: list[CorpusPackage] = []
        for rule in self.rules:
            packages.extend(rule.packages)
        return packages

    @property
    def implemented_packages(self) -> list[str]:
        """Get the implemented packages."""
        implemented_packages: list[str] = []
        for rule in self.rules:
            for package in rule.packages:
                if package.has_directory:
                    implemented_packages.append(package.name)
        return implemented_packages

    @classmethod
    def from_test_case(cls, test_case_path: Path) -> 'CorpusTestCase':
        test_case_schema: etree.XMLSchema = etree.XMLSchema(etree.parse(test_case_path / 'testCase.xsd'))
        is_xml_valid: bool = test_case_schema.validate(etree.parse(test_case_path / 'testCase.xml'))
        test_case: TestCase = XmlParser().from_path(test_case_path / 'testCase.xml' , TestCase)
        return CorpusTestCase(
            id=test_case.id.requirement_id,
            description=test_case.description.value,
            is_xml_valid=is_xml_valid,
            testable=Testable.from_str(test_case.testable.value),
            rules=[CorpusRule.from_rule(rule, test_case_path) for rule in test_case.rules.rule] if test_case.rules is not None else [],
            xml_validation_error= "" if is_xml_valid else test_case_schema.error_log.last_error.message)

class Corpus(BaseModel):
    path: Path
    specification: Specification
    test_cases: list[CorpusTestCase] = []

    @computed_field
    def rules(self) -> list[CorpusRule]:
        """Get the rules from the specification."""
        rules: list[CorpusRule] = []
        for test_case in self.test_cases:
            if (test_case.testable and test_case.rules is not None):
                # Only add rules if the test case is testable and has rules
                rules.extend(test_case.rules)
        return rules

    @property
    def packages(self) -> list[CorpusPackage]:
        """Get the rules from the specification."""
        packages: list[CorpusPackage] = []
        for test_case in self.test_cases:
            if (test_case.testable and test_case.rules is not None):
                for rule in test_case.rules:
                    packages.extend(rule.packages)
        return packages
    
    @property
    def implemented_packages(self) -> list[str]:
        """Get the implemented packages."""
        implemented_packages: list[str] = []
        for test_case in self.test_cases:
            implemented_packages.extend(test_case.implemented_packages)
        return list(set(implemented_packages))  # Remove duplicates

    @classmethod
    def from_directory(cls, specification:Specification, corpus_path: Path) -> 'Corpus':
        """Create a Corpus from a directory."""
        test_cases: list[CorpusTestCase] = []
        for test_case_path in corpus_path.iterdir():
            if test_case_path.is_dir() and test_case_path.name.startswith(specification.id):
                test_cases.append(CorpusTestCase.from_test_case(test_case_path))

        corpus = Corpus(path=corpus_path, specification=specification, test_cases=test_cases)
        return corpus