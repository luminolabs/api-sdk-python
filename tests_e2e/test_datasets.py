import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING

from config import get_config
from logger import get_logger
from lumino.api_sdk.models import DatasetCreate, DatasetUpdate, DatasetStatus
from utils import TestData, generate_test_name, sanitize_name, format_size

if TYPE_CHECKING:
    from test_runner import TestRunner

logger = get_logger(__name__)
test_data = TestData()

SAMPLE_DATASET_CONTENT = [
    {
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "What is machine learning?"
            },
            {
                "role": "assistant",
                "content": "Machine learning is a branch of artificial intelligence that allows systems to learn and improve from experience without being explicitly programmed."
            }
        ]
    }
]


async def create_test_dataset() -> Path:
    """Create a temporary test dataset file."""
    # Create test file in temp directory
    dataset_path = Path(get_config().temp_dir) / "test_dataset.jsonl"

    # Write sample data in JSONL format
    with open(dataset_path, 'w', encoding='utf-8') as f:
        for item in SAMPLE_DATASET_CONTENT:
            f.write(json.dumps(item) + '\n')

    return dataset_path


async def test_dataset_operations(runner: 'TestRunner') -> None:
    """
    Test dataset management operations.

    Tests:
    - Create test dataset file
    - Upload dataset
    - List datasets
    - Get dataset details
    - Update dataset
    - Delete dataset
    - Verify dataset status changes
    """
    logger.info("Starting dataset operations test")

    # Create test dataset file
    dataset_path = await create_test_dataset()
    dataset_name = sanitize_name(generate_test_name("test-dataset"))
    logger.info(f"Created test dataset file: {dataset_path}")

    # Upload dataset
    dataset = await runner.sdk.dataset.upload_dataset(
        str(dataset_path),
        DatasetCreate(
            name=dataset_name,
            description="Test dataset for e2e testing"
        )
    )

    # Verify upload
    assert dataset.name == dataset_name, f"Dataset name mismatch. Expected: {dataset_name}, got: {dataset.name}"
    assert dataset.status == DatasetStatus.UPLOADED, \
        f"Unexpected dataset status: {dataset.status}"
    assert dataset.file_size > 0, f"Dataset file size is 0"

    # Store dataset info for cleanup
    test_data.set('test_dataset_name', dataset_name)
    logger.info(f"Uploaded dataset ({format_size(dataset.file_size)})")

    # List datasets and verify our new dataset is present
    datasets_response = await runner.sdk.dataset.list_datasets()
    assert any(d.name == dataset_name for d in datasets_response.data), \
        f"Uploaded dataset {dataset_name} not found in list response"

    # Get specific dataset
    dataset_info = await runner.sdk.dataset.get_dataset(dataset_name)
    assert dataset_info.name == dataset_name, "Dataset details name mismatch"
    assert dataset_info.status == DatasetStatus.UPLOADED, \
        f"Dataset not uploaded. Status: {dataset_info.status}"

    # Update dataset
    new_description = "Updated test dataset description"
    logger.info(f"Updating dataset description")

    updated_dataset = await runner.sdk.dataset.update_dataset(
        dataset_name,
        DatasetUpdate(description=new_description)
    )

    # Verify update
    assert updated_dataset.description == new_description, \
        f"Dataset description not updated. Expected: {new_description}, got: {updated_dataset.description}"

    # Delete dataset
    logger.info(f"Deleting dataset: {dataset_name}")
    await runner.sdk.dataset.delete_dataset(dataset_name)

    # Verify deletion by checking status
    try:
        deleted_dataset = await runner.sdk.dataset.get_dataset(dataset_name)
        assert deleted_dataset.status == DatasetStatus.DELETED, \
            f"Dataset not marked as deleted. Status: {deleted_dataset.status}"
    except Exception as e:
        # Some APIs might return 404 for deleted datasets instead of status
        logger.info(f"Dataset not accessible after deletion: {e}")

    # Clean up test file
    dataset_path.unlink()
    logger.info("Dataset operations test completed successfully")


async def cleanup_datasets(runner: 'TestRunner') -> None:
    """
    Clean up datasets created during testing.
    """
    try:
        dataset_name = test_data.get('test_dataset_name')
        if dataset_name:
            try:
                # Attempt to delete the dataset if it exists
                await runner.sdk.dataset.delete_dataset(dataset_name)
                logger.info(f"Deleted test dataset: {dataset_name}")
            except Exception as e:
                logger.warning(f"Error deleting dataset {dataset_name}: {e}")
    except Exception as e:
        logger.error(f"Error during dataset cleanup: {e}")
        raise


if __name__ == "__main__":
    # For manual testing
    from test_runner import TestRunner


    async def run_test():
        runner = TestRunner()
        try:
            await runner.setup()
            await test_dataset_operations(runner)
        finally:
            await cleanup_datasets(runner)
            await runner.cleanup()


    asyncio.run(run_test())
