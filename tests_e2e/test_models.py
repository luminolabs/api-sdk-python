import asyncio
from typing import TYPE_CHECKING

from logger import get_logger
from lumino.api_sdk.models import BaseModelStatus, FineTunedModelStatus
from utils import TestData

if TYPE_CHECKING:
    from test_runner import TestRunner

logger = get_logger(__name__)
test_data = TestData()


async def test_model_operations(runner: 'TestRunner') -> None:
    """
    Test model listing and information retrieval.

    Tests:
    - List base models
    - Get base model details
    - List fine-tuned models
    - Get fine-tuned model details
    """
    logger.info("Starting model operations test")

    # List base models
    base_models = await runner.sdk.model.list_base_models()
    assert len(base_models.data) > 0, "No base models available"

    # Store first active model for other tests
    active_models = [m for m in base_models.data if m.status == BaseModelStatus.ACTIVE]
    assert len(active_models) > 0, "No active base models found"
    test_data.set('base_model', active_models[0])

    logger.info(f"Found {len(base_models.data)} base models, {len(active_models)} active")

    # Get specific base model details
    base_model = await runner.sdk.model.get_base_model(active_models[0].name)
    assert base_model.status == BaseModelStatus.ACTIVE, \
        f"Base model not active: {base_model.status}"

    # List fine-tuned models
    ft_models = await runner.sdk.model.list_fine_tuned_models()
    logger.info(f"Found {len(ft_models.data)} fine-tuned models")

    # If there are any fine-tuned models, test getting details
    if ft_models.data:
        active_ft_models = [
            m for m in ft_models.data
            if m.status == FineTunedModelStatus.ACTIVE
        ]
        if active_ft_models:
            model = active_ft_models[0]
            model_details = await runner.sdk.model.get_fine_tuned_model(model.name)
            assert model_details.artifacts is not None, "Model missing artifacts"
            logger.info(f"Retrieved details for model: {model.name}")

    logger.info("Model operations test completed successfully")


if __name__ == "__main__":
    # For manual testing
    from test_runner import TestRunner


    async def run_test():
        runner = TestRunner()
        try:
            await runner.setup()
            await test_model_operations(runner)
        finally:
            await runner.cleanup()


    asyncio.run(run_test())
