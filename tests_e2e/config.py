import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console

# Get project root directory
ROOT_DIR = Path(__file__).parent.resolve()
TEMP_DIR = ROOT_DIR / ".temp"


def is_truthy(value: str | bool) -> bool:
    """
    Check if a value is truthy.

    Args:
        value: Value to check

    Returns:
        True if value is truthy, False otherwise
    """
    if isinstance(value, str):
        return value.lower() in ['true', 'yes', 'on', '1']
    elif isinstance(value, bool):
        return value
    return False


@dataclass
class Config:
    """
    Configuration settings for E2E tests.
    Loads from environment variables with fallbacks to default values.
    """
    api_key: str
    api_url: str = "https://api.luminolabs.ai/v1"
    run_with_scheduler: bool = False
    log_level: str = "INFO"
    temp_dir: Path = TEMP_DIR
    fine_tuning_base_model: str = "llm_dummy"

    @classmethod
    def load(cls, env_file: Optional[str] = None) -> 'Config':
        """
        Load configuration from environment variables, with optional .env file.

        Args:
            env_file: Optional path to .env file. If not provided, looks for .env in project root.

        Returns:
            Config object with loaded settings

        Raises:
            ValueError: If required settings are missing
        """
        # Load .env file if provided or exists in root directory
        if env_file:
            load_dotenv(env_file)
        else:
            default_env = ROOT_DIR / ".env"
            if default_env.exists():
                load_dotenv(default_env)

        # Get required API key
        api_key = os.getenv("LUMSDK_API_KEY")
        if not api_key:
            raise ValueError(
                "LUMSDK_API_KEY environment variable is required. "
                "Set it in .env file or as environment variable."
            )

        # Get optional settings with defaults
        return cls(
            api_key=api_key,
            api_url=os.getenv("LUMSDK_BASE_URL", cls.api_url),
            run_with_scheduler=is_truthy(os.getenv("E2E_TESTS_RUN_WITH_SCHEDULER", cls.run_with_scheduler)),
            log_level=os.getenv("E2E_TESTS_LOG_LEVEL", cls.log_level),
            fine_tuning_base_model=os.getenv("E2E_TESTS_FINE_TUNING_BASE_MODEL", cls.fine_tuning_base_model)
        )

    def validate(self) -> None:
        """
        Validate the configuration settings.

        Raises:
            ValueError: If any settings are invalid
        """
        # Validate API key format (basic check)
        if not isinstance(self.api_key, str) or len(self.api_key) < 10:
            raise ValueError("Invalid API key format")

        # Validate API URL format
        if not self.api_url.startswith(("http://", "https://")):
            raise ValueError("API URL must start with http:// or https://")

        # Validate log level
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_log_levels)}")

        # Validate temp directory
        if not self.temp_dir.exists():
            os.makedirs(self.temp_dir, exist_ok=True)

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()

    def log_config(self, console: Console) -> None:
        """Print the configuration settings."""
        console.print("\n=== Configuration Settings ===")
        console.print(f"API URL: {self.api_url}")
        console.print(f"Run with scheduler: {self.run_with_scheduler}")
        console.print(f"Log Level: {self.log_level}")
        console.print(f"Temp Directory: {self.temp_dir}")
        console.print(f"Fine-tuning Base Model: {self.fine_tuning_base_model}\n")


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance, creating it if necessary.

    Returns:
        Config object with current settings
    """
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def initialize_config(env_file: Optional[str] = None) -> Config:
    """
    Initialize or reinitialize the global configuration.

    Args:
        env_file: Optional path to .env file

    Returns:
        Newly created Config object

    Note:
        This will replace any existing configuration.
    """
    global _config
    _config = Config.load(env_file)
    return _config


if __name__ == "__main__":
    # Example usage and validation of configuration
    try:
        config = initialize_config()
        print(f"Configuration loaded successfully:")
        print(f"API URL: {config.api_url}")
        print(f"Run with scheduler: {config.run_with_scheduler}")
        print(f"Log Level: {config.log_level}")
        print(f"Temp Directory: {config.temp_dir}")
        print(f"Fine-tuning Base Model: {config.fine_tuning_base_model}")
    except ValueError as e:
        print(f"Configuration error: {e}")
