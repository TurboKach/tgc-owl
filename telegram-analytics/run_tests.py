#!/usr/bin/env python3
"""
Unified test runner for Telegram Analytics Bot.
Provides easy commands to run different types of tests.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False
    except FileNotFoundError:
        print(f"❌ {description} - FAILED (command not found)")
        return False


def run_unit_tests(verbose: bool = False, coverage: bool = False) -> bool:
    """Run unit tests with pytest."""
    cmd = ["uv", "run", "pytest"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=src/telegram_analytics", "--cov-report=term-missing"])

    cmd.append("tests/")

    return run_command(cmd, "Unit Tests")


def run_linting() -> bool:
    """Run code linting with ruff."""
    commands = [
        (["uv", "run", "ruff", "check", "src/", "tests/"], "Linting (ruff check)"),
        (
            ["uv", "run", "black", "--check", "src/", "tests/"],
            "Code formatting (black check)",
        ),
    ]

    all_passed = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            all_passed = False

    return all_passed


def run_type_checking() -> bool:
    """Run type checking with mypy."""
    return run_command(
        ["uv", "run", "mypy", "src/telegram_analytics/"], "Type Checking (mypy)"
    )


def run_all_internal_tests(verbose: bool = False, coverage: bool = False) -> bool:
    """Run all internal tests (unit tests, linting, type checking)."""
    print("🚀 Running All Internal Tests")
    print("=" * 60)

    results = []

    # Run unit tests
    results.append(run_unit_tests(verbose, coverage))

    # Run linting
    results.append(run_linting())

    # Run type checking
    results.append(run_type_checking())

    # Summary
    passed = sum(results)
    total = len(results)

    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    if all(results):
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        return True
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
        return False


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Unified test runner for Telegram Analytics Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all internal tests
  python run_tests.py --unit             # Run only unit tests
  python run_tests.py --unit --verbose   # Run unit tests with verbose output
  python run_tests.py --unit --coverage  # Run unit tests with coverage
  python run_tests.py --lint             # Run only linting
  python run_tests.py --type             # Run only type checking
        """,
    )

    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--lint", action="store_true", help="Run only linting checks")
    parser.add_argument("--type", action="store_true", help="Run only type checking")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output for tests"
    )
    parser.add_argument(
        "--coverage", "-c", action="store_true", help="Run tests with coverage report"
    )

    args = parser.parse_args()

    # If no specific test type is specified, run all
    if not any([args.unit, args.lint, args.type]):
        success = run_all_internal_tests(args.verbose, args.coverage)
    else:
        success = True

        if args.unit:
            success &= run_unit_tests(args.verbose, args.coverage)

        if args.lint:
            success &= run_linting()

        if args.type:
            success &= run_type_checking()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
