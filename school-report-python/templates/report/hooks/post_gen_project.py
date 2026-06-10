#!/usr/bin/env python
"""Post-generation hook for the report cookiecutter template."""

import os
import sys

# Get cookiecutter variables
report_id = "{{ cookiecutter.report_id }}"
report_name = "{{ cookiecutter.report_name }}"
has_parameters = "{{ cookiecutter.has_parameters }}"

# ANSI colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def main():
    """Run post-generation tasks."""
    print(f"\n{GREEN}{BOLD}Report '{report_id}' created successfully!{RESET}\n")

    # Validation warnings
    warnings = []

    if report_id != report_id.upper():
        warnings.append(
            f"Report ID '{report_id}' should be uppercase. "
            f"Consider renaming to '{report_id.upper()}'."
        )

    if len(report_id) < 2:
        warnings.append("Report ID is very short. Consider using a more descriptive name.")

    if warnings:
        print(f"{YELLOW}{BOLD}Warnings:{RESET}")
        for warning in warnings:
            print(f"  {YELLOW}- {warning}{RESET}")
        print()

    # Next steps
    print(f"{BLUE}{BOLD}Next steps:{RESET}")
    print(f"  1. Edit {BOLD}report.yaml{RESET} to configure your report definition")
    print(f"  2. Add your SQL queries to {BOLD}queries/{RESET}")
    print(f"  3. Customize the Typst template in {BOLD}template/main.typ{RESET}")
    print(f"  4. Validate your report:")
    print(f"     {BOLD}schoolreport reports validate {report_id}{RESET}")
    print(f"  5. Test data fetching:")
    print(f"     {BOLD}schoolreport generate {report_id} --data-only{RESET}")
    print(f"  6. Generate the full report:")
    print(f"     {BOLD}schoolreport generate {report_id}{RESET}")
    print()

    # Show report structure
    print(f"{BLUE}{BOLD}Created files:{RESET}")
    print(f"  reports/{report_id}/")
    print(f"  ├── report.yaml           # Report definition")
    print(f"  ├── queries/")
    print(f"  │   └── example_query.sql # Example SQL query")
    print(f"  └── template/")
    print(f"      ├── main.typ          # Typst template")
    print(f"      └── assets/           # Assets directory")
    print()


if __name__ == "__main__":
    main()
