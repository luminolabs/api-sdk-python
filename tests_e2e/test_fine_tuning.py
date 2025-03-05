import asyncio
from typing import TYPE_CHECKING

from test_datasets import create_test_dataset

from logger import get_logger
from lumino.api_sdk.models import (
    FineTuningJobCreate,
    FineTuningJobParameters,
    FineTuningJobType,
    ComputeProvider,
    FineTuningJobStatus,
    DatasetCreate
)
from utils import TestData, generate_test_name, sanitize_name, wait_for_condition

if TYPE_CHECKING:
    from test_runner import TestRunner

logger = get_logger(__name__)
test_data = TestData()


async def test_fine_tuning_operations(runner: 'TestRunner') -> None:
    """
    Test fine-tuning operations.

    Tests:
    - List available base models
    - Create dataset for fine-tuning
    - Create fine-tuning job
    - Monitor job progress
    - List fine-tuned models
    - Get model details
    - Cancel job (if still running)
    - Delete job and cleanup
    """
    logger.info("Starting fine-tuning operations test")

    # First, get available base models
    models_response = await runner.sdk.model.list_base_models()
    assert len(models_response.data) > 0, "No base models available"

    base_model = runner.config.fine_tuning_base_model
    # See if the base model is available, except if it's "llm_dummy"
    if base_model != "llm_dummy":
        model_exists = any(m.name == base_model for m in models_response.data)
        assert model_exists, f"Base model {base_model} not found in available models"
    logger.info(f"Using base model: {base_model}")

    # Create test dataset
    dataset_name = sanitize_name(generate_test_name("ft-dataset"))
    dataset_path = await create_test_dataset()  # From test_datasets.py

    await runner.sdk.dataset.upload_dataset(
        str(dataset_path),
        DatasetCreate(
            name=dataset_name,
            description="Dataset for fine-tuning test"
        )
    )
    test_data.set('test_dataset_name', dataset_name)
    logger.info(f"Uploaded dataset: {dataset_name}")

    # Create fine-tuning job
    job_name = sanitize_name(generate_test_name("ft-job"))
    logger.info(f"Creating fine-tuning job: {job_name}")

    job = await runner.sdk.fine_tuning.create_fine_tuning_job(
        FineTuningJobCreate(
            base_model_name=base_model,
            dataset_name=dataset_name,
            name=job_name,
            type=FineTuningJobType.LORA,  # Use LORA for faster training
            provider=ComputeProvider.GCP,
            parameters=FineTuningJobParameters(
                batch_size=2,
                shuffle=True,
                num_epochs=1,
                lr=3e-4
            )
        )
    )

    # Store job info for cleanup
    test_data.set('test_job_name', job_name)
    logger.info(f"Created fine-tuning job {job_name} with ID: {job.id}")

    if runner.config.run_with_scheduler:
        # Monitor job progress
        await monitor_job_progress(runner, job_name)

    # List fine-tuning jobs and verify our job is present
    jobs_response = await runner.sdk.fine_tuning.list_fine_tuning_jobs()
    job_found = False
    for listed_job in jobs_response.data:
        if listed_job.name == job_name:
            job_found = True
            assert listed_job.base_model_name == base_model, \
                "Base model name mismatch in job listing"
            assert listed_job.dataset_name == dataset_name, \
                "Dataset name mismatch in job listing"
            break
    assert job_found, f"Created job {job_name} not found in list response"

    # Get detailed job information
    job_details = await runner.sdk.fine_tuning.get_fine_tuning_job(job_name)
    assert job_details.parameters is not None, "Job parameters missing in details"
    assert job_details.parameters["batch_size"] == 2, "Job parameter mismatch"

    # If job is still running, test cancellation
    if job_details.status == FineTuningJobStatus.RUNNING:
        logger.info(f"Cancelling job {job_name}")
        cancelled_job = await runner.sdk.fine_tuning.cancel_fine_tuning_job(job_name)
        assert cancelled_job.status in (FineTuningJobStatus.STOPPING, FineTuningJobStatus.STOPPED), \
            f"Job not cancelled. Status: {cancelled_job.status}"

    # Check for created models if job completed successfully
    if job_details.status == FineTuningJobStatus.COMPLETED:
        models_response = await runner.sdk.model.list_fine_tuned_models()
        models = [m for m in models_response.data if m.fine_tuning_job_name == job_name]
        if models:
            test_data.set('test_model_name', models[0].name)
            logger.info(f"Fine-tuned model created: {models[0].name}")

    # Delete the job
    logger.info(f"Deleting job {job_name}")
    await runner.sdk.fine_tuning.delete_fine_tuning_job(job_name)

    logger.info("Fine-tuning operations test completed successfully")


async def monitor_job_progress(runner: 'TestRunner', job_name: str) -> None:
    """
    Monitor fine-tuning job progress until completion or timeout.

    Args:
        runner: TestRunner instance
        job_name: Name of the job to monitor
    """
    terminal_statuses = {
        FineTuningJobStatus.COMPLETED,
        FineTuningJobStatus.FAILED,
        FineTuningJobStatus.STOPPED,
        FineTuningJobStatus.DELETED
    }

    last_step = -1
    last_status = None

    async def check_progress():
        nonlocal last_step, last_status

        job = await runner.sdk.fine_tuning.get_fine_tuning_job(job_name)

        # Log progress if changed
        if job.status != last_status:
            logger.info(f"Job status: {job.status}")
            last_status = job.status

        if job.current_step != last_step and job.current_step is not None:
            progress = (job.current_step / job.total_steps * 100) if job.total_steps else 0
            logger.info(
                f"Progress: {job.current_step}/{job.total_steps} steps "
                f"({progress:.1f}%) - Epoch {job.current_epoch}/{job.total_epochs}"
            )
            last_step = job.current_step

        if job.status == FineTuningJobStatus.FAILED:
            error_msg = f"Job failed: {job.error}" if hasattr(job, 'error') else "Job failed"
            raise RuntimeError(error_msg)

        return job.status in terminal_statuses

    await wait_for_condition(
        check_progress,
        timeout=120,  # 2 minutes should be enough for dummy job
        interval=5.0,
        message=f"Job {job_name} did not complete within 120 seconds"
    )


async def cleanup_fine_tuning(runner: 'TestRunner') -> None:
    """
    Clean up fine-tuning test temp files.
    """
    try:
        # Clean up job
        job_name = test_data.get('test_job_name')
        if job_name:
            try:
                await runner.sdk.fine_tuning.delete_fine_tuning_job(job_name)
                logger.info(f"Deleted test job: {job_name}")
            except Exception as e:
                logger.warning(f"Error deleting job {job_name}: {e}")

        # Clean up dataset
        dataset_name = test_data.get('test_dataset_name')
        if dataset_name:
            try:
                await runner.sdk.dataset.delete_dataset(dataset_name)
                logger.info(f"Deleted test dataset: {dataset_name}")
            except Exception as e:
                logger.warning(f"Error deleting dataset {dataset_name}: {e}")

        # Note: Fine-tuned models are automatically cleaned up when the job is deleted

    except Exception as e:
        logger.error(f"Error during fine-tuning cleanup: {e}")
        raise


if __name__ == "__main__":
    # For manual testing
    from test_runner import TestRunner


    async def run_test():
        runner = TestRunner()
        try:
            await runner.setup()
            await test_fine_tuning_operations(runner)
        finally:
            await cleanup_fine_tuning(runner)
            await runner.cleanup()


    asyncio.run(run_test())
