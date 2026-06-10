#!/usr/bin/env python
"""
Pre-generation hook for cookiecutter template.

Validates input and performs pre-generation checks.
"""

import re
import sys


def validate_report_id(report_id: str) -> None:
    """Validate report ID format."""
    # Format: ATS-XX, ATM, ATSBR, etc (letters, numbers, hyphens)
    pattern = r'^[A-Z0-9]+(-[A-Z0-9]+)*$'
    if not re.match(pattern, report_id):
        print(f"ERROR: Report ID '{report_id}' is invalid!")
        print("Expected format: Uppercase letters, numbers, and hyphens (e.g., ATS-02, ATM, ATSBR)")
        sys.exit(1)


def main():
    """Run pre-generation checks."""
    report_id = '{{ cookiecutter.report_id }}'

    print("=" * 60)
    print("SEGAPE School Report - New Report Generator")
    print("=" * 60)
    print(f"Creating report: {report_id}")
    print(f"Name: {{ cookiecutter.report_name }}")
    print(f"Version: {{ cookiecutter.report_version }}")
    print()

    # Validate report ID
    validate_report_id(report_id)

    print("✓ Pre-generation checks passed!")
    print()


if __name__ == "__main__":
    main()
