import asyncio
import random
import string
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Awaitable, List, Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from config import get_config, Config
from logger import get_logger
from lumino.api_sdk.sdk import LuminoSDK

logger = get_logger(__name__)
console = Console()


@dataclass
class TestResult:
    """Represents the result of a single test."""
    name: str
    success: bool
    error: Optional[Exception] = None
    duration: float = 0.0

    @property
    def status_str(self) -> str:
        return "✓ PASS" if self.success else "✗ FAIL"

    @property
    def duration_str(self) -> str:
        return f"{self.duration:.2f}s"


class TestRunner:
    """Main test orchestration class."""

    def __init__(self):
        self.config: Config = get_config()
        self.sdk: Optional[LuminoSDK] = None
        self.results: List[TestResult] = []
        self._test_run_id = self._generate_run_id()

    @staticmethod
    def _generate_run_id(length: int = 8) -> str:
        """Generate a unique test run identifier."""
        chars = string.ascii_lowercase + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def _format_error(error: Exception) -> str:
        """Format error details for display."""
        return f"{type(error).__name__}: {str(error)}"

    async def _run_test(
            self,
            test_func: Callable[['TestRunner'], Awaitable[None]],
            progress: Progress
    ) -> TestResult:
        """Run a single test with progress tracking."""
        test_name = test_func.__name__
        task = progress.add_task(f"Running {test_name}...", total=None)
        start_time = time.time()

        try:
            await test_func(self)
            success = True
            error = None
        except Exception as e:
            logger.exception(f"Test {test_name} failed")
            success = False
            error = e
        finally:
            duration = time.time() - start_time
            progress.remove_task(task)

        return TestResult(test_name, success, error, duration)

    def print_results(self) -> None:
        """Print test results in a formatted table."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed

        console.print("=== Test Results ===")
        console.print(f"Run ID: {self._test_run_id}")
        console.print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        console.print(f"Total: {total}, Passed: {passed}, Failed: {failed}\n")

        # Print individual test results
        for result in self.results:
            color = "green" if result.success else "red"
            status_str = f"[{color}]{result.status_str}[/{color}]"
            console.print(f"{status_str} {result.name} ({result.duration_str})")
            if result.error:
                console.print(f"  [red]Error: {self._format_error(result.error)}[/red]")

    async def setup(self) -> None:
        """Initialize test environment."""
        # Log configuration
        self.config.log_config(console)

        # Initialize SDK
        self.sdk = LuminoSDK(self.config.api_key, self.config.api_url)
        await self.sdk.__aenter__()

    async def cleanup(self) -> None:
        """Cleanup test environment."""
        if self.sdk:
            # Close SDK connection
            await self.sdk.__aexit__(None, None, None)

    async def run_tests(self) -> bool:
        """
        Run all tests and return overall success status.

        Returns:
            bool: True if all tests passed, False otherwise
        """
        try:
            await self.setup()

            # Import test modules here to avoid circular imports
            from test_users import test_user_operations
            from test_api_keys import test_api_key_operations
            from test_datasets import test_dataset_operations
            from test_models import test_model_operations
            from test_fine_tuning import test_fine_tuning_operations
            from test_usage import test_usage_operations
            from test_billing import test_billing_operations

            console.print("=== Running tests ===")

            # Define test sequence
            tests = [
                test_user_operations,
                test_api_key_operations,
                test_dataset_operations,
                test_model_operations,
                test_fine_tuning_operations,
                test_usage_operations,
                test_billing_operations
            ]

            # Create progress display
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console
            )

            # Run tests
            with progress:
                for test in tests:
                    result = await self._run_test(test, progress)
                    self.results.append(result)

            # Print results
            self.print_results()

            return all(result.success for result in self.results)

        except Exception as e:
            logger.exception("Test run failed")
            console.print(f"[red]Test run failed: {str(e)}[/red]")
            return False

        finally:
            await self.cleanup()


async def main() -> int:
    """
    Main entry point for test runner.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    runner = TestRunner()
    success = await runner.run_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
