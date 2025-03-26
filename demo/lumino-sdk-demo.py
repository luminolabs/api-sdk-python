# 1. Head to https://api.luminolabs.ai, log in, and create an API key.
#
# 2. On your terminal:
#    a. Go to the `demo` directory: `cd demo`
#    a. Install the SDK using pip: `pip install lumino-api-sdk-python`
#    b. Export the API key as an environment variable: `export LUMSDK_API_KEY=your-api-key`
#    c. Run your code: `python lumino-sdk-demo.py`


import asyncio
import os
import time

from lumino.api_sdk.models import FineTuningJobParameters, FineTuningJobCreate, DatasetCreate, FineTuningJobType, \
    ComputeProvider, FineTuningJobStatus
from lumino.api_sdk.sdk import LuminoSDK


async def main():
    print("Starting Lumino SDK demo...")

    suffix = str(int(time.time()) % 10000)  # 4 digit random number
    dataset_name = "text2sql-" + suffix

    async with LuminoSDK(os.environ.get("LUMSDK_API_KEY")) as client:
        # Upload a dataset
        r = await client.dataset.upload_dataset("./text2sql.jsonl", DatasetCreate(
            name=dataset_name,
            description="Text to SQL dataset"
        ))

        # Confirm the dataset was uploaded
        datasets = (await client.dataset.list_datasets()).data
        print("\n=== Dataset: ===")
        print(datasets[:1])

        # Create a fine-tuning job
        job = await client.fine_tuning.create_fine_tuning_job(FineTuningJobCreate(
            base_model_name="llm_llama3_2_1b",  # Use a smaller model for faster fine-tuning
            dataset_name=dataset_name,
            name="text2sql-fine-tuning-" + suffix,
            type=FineTuningJobType.LORA,
            parameters=FineTuningJobParameters(
                batch_size=8,
                shuffle=True,
                num_epochs=1,
            ),
            provider=ComputeProvider.GCP
        ))
        print("\n=== Fine-tuning job created: ===")
        print(job)

        # Monitor the fine-tuning job
        while job.status != FineTuningJobStatus.COMPLETED:
            job = await client.fine_tuning.get_fine_tuning_job(job.name)
            print("\n=== Fine-tuning job details: ===")
            print(job)
            await asyncio.sleep(5)

        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
