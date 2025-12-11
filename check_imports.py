#!/usr/bin/env python3
"""
Import Path Checker

This script checks all Python files in the project for old import paths
that need to be updated after restructuring.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path so we can import app module
sys.path.insert(0, str(Path(__file__).parent))

# Old import patterns to search for
OLD_IMPORT_PATTERNS = [
    (r"from database import", "from app.models.database import"),
    (r"from scraper import", "from app.scraper.chewy_scraper import"),
    (r"from config import", "from app.config import"),
    (r"import database", "from app.models import database"),
    (r"import scraper", "from app.scraper import chewy_scraper"),
    (r"import config", "from app import config"),
]

# Directories to check
DIRECTORIES_TO_CHECK = [
    "app",
    "scripts",
    "tests",
]

# Files to exclude
EXCLUDE_PATTERNS = [
    "__pycache__",
    ".venv",
    ".git",
    "*.pyc",
    ".pytest_cache",
]


def should_exclude(file_path: str) -> bool:
    """Check if file should be excluded from checking"""
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file_path:
            return True
    return False


def find_old_imports(file_path: str) -> List[Tuple[int, str, str]]:
    """
    Find old import patterns in a file.

    Returns:
        List of tuples (line_number, old_pattern, suggested_replacement)
    """
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                for old_pattern, new_pattern in OLD_IMPORT_PATTERNS:
                    if re.search(old_pattern, line):
                        issues.append((line_num, line.strip(), new_pattern))
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")

    return issues


def check_project() -> bool:
    """
    Check all Python files in the project for old imports.

    Returns:
        True if issues found, False otherwise
    """
    print("🔍 Checking for old import paths...\n")

    total_files = 0
    files_with_issues = 0
    total_issues = 0

    for directory in DIRECTORIES_TO_CHECK:
        if not os.path.exists(directory):
            print(f"⚠️  Directory not found: {directory}")
            continue

        print(f"📁 Checking {directory}/")

        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)

                if should_exclude(file_path):
                    continue

                total_files += 1
                issues = find_old_imports(file_path)

                if issues:
                    files_with_issues += 1
                    total_issues += len(issues)

                    print(f"\n❌ {file_path}")
                    for line_num, old_line, suggestion in issues:
                        print(f"   Line {line_num}: {old_line}")
                        print(f"   Suggested: {suggestion}")

    print(f"\n{'=' * 70}")
    print(f"📊 Summary:")
    print(f"   Total files checked: {total_files}")
    print(f"   Files with issues: {files_with_issues}")
    print(f"   Total issues found: {total_issues}")

    if total_issues > 0:
        print(f"\n⚠️  Found {total_issues} import(s) that need updating!")
        return True
    else:
        print(f"\n✅ All imports look good!")
        return False


def check_specific_files() -> None:
    """Check specific files that are known to need updates"""
    print("\n" + "=" * 70)
    print("🎯 Checking specific files that may need updates:\n")

    files_to_check = [
        "app/scraper/monitor.py",
        "app/scraper/distribute_work.py",
        "app/scraper/export_data.py",
        "app/scraper/import_data.py",
        "scripts/scrape_products.py",
    ]

    for file_path in files_to_check:
        if os.path.exists(file_path):
            issues = find_old_imports(file_path)
            status = "✅" if not issues else "❌"
            issue_count = f"({len(issues)} issues)" if issues else ""
            print(f"{status} {file_path} {issue_count}")

            if issues:
                for line_num, old_line, suggestion in issues:
                    print(f"     Line {line_num}: {old_line}")
                    print(f"     → {suggestion}")
        else:
            print(f"⚠️  {file_path} - File not found")


def check_api_startup() -> None:
    """Check if the API can be imported without errors"""
    print("\n" + "=" * 70)
    print("🚀 Testing API module imports:\n")

    try:
        print("   Importing app.config...", end=" ")
        from app import config

        print("✅")
    except ImportError as e:
        print(f"❌\n      Error: {e}")

    try:
        print("   Importing app.models.database...", end=" ")
        from app.models import database

        print("✅")
    except ImportError as e:
        print(f"❌\n      Error: {e}")

    try:
        print("   Importing app.models.product...", end=" ")
        from app.models import product

        print("✅")
    except ImportError as e:
        print(f"❌\n      Error: {e}")

    try:
        print("   Importing app.models.score...", end=" ")
        from app.models import score

        print("✅")
    except ImportError as e:
        print(f"❌\n      Error: {e}")

    try:
        print("   Importing app.services.product_service...", end=" ")
        from app.services import product_service

        print("✅")
    except ImportError as e:
        print(f"❌\n      Error: {e}")

    try:
        print("   Importing app.services.scoring_service...", end=" ")
        from app.services import scoring_service

        print("✅")
    except ImportError as e:
        print(f"❌\n      Error: {e}")

    try:
        print("   Importing app.main...", end=" ")
        from app import main

        print("✅")
    except ImportError as e:
        print(f"❌\n      Error: {e}")


def main():
    """Main function"""
    print("=" * 70)
    print("🔧 Dog Food Scoring API - Import Path Checker")
    print("=" * 70)
    print()

    # Check for old import patterns
    has_issues = check_project()

    # Check specific files
    check_specific_files()

    # Try importing modules
    check_api_startup()

    print("\n" + "=" * 70)

    if has_issues:
        print("❌ Action Required: Update the import paths shown above")
        print("\nQuick fix pattern:")
        print("  from database import X  →  from app.models.database import X")
        print("  from scraper import X   →  from app.scraper.chewy_scraper import X")
        print("  from config import X    →  from app.config import X")
    else:
        print("✅ All import paths look good!")
        print("🚀 You can proceed with starting the API server")

    print("=" * 70)


if __name__ == "__main__":
    main()
