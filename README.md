# Lumino SDK for Python

[![Static Badge](https://img.shields.io/badge/pypi-0.11.0-blue)](https://pypi.org/project/lumino/)
[![](https://dcbadge.limes.pink/api/server/https://discord.gg/62DThqunWx?style=flat&compact=true)](https://discord.gg/https://discord.gg/62DThqunWx)
[![X (formerly Twitter) Follow](https://img.shields.io/twitter/follow/luminoai)](https://x.com/luminoai)

The Lumino SDK for Python provides a convenient way to interact with the Lumino API for managing large language model (LLM) fine-tuning processes and related resources.

## Features

- User management
- API key management
- Dataset operations
- Fine-tuning job management
- Model information retrieval
- Usage tracking

## Installation

You can install the Lumino SDK using pip:

```bash
pip install lumino-api-sdk-python
```

## Setting up API Key

Generate an API key by visiting the Lumino Dashboard at this [settings page](https://app.luminolabs.ai/settings).

## Setting environment variable

```
export LUMSDK_API_KEY=xxxxx
```

## Usage – Python Client

### User Management

```python
import os
import asyncio
from lumino.api_sdk.sdk import LuminoSDK


async def main():
    async with LuminoSDK(os.environ.get("LUMSDK_API_KEY")) as client:
        user = await client.user.get_current_user()
        print(user)


asyncio.run(main())
```

### Datasets
The files API is used for fine-tuning and allows developers to upload data to fine-tune on. It also has several methods to list all files, retrive files, and delete files. Please refer to our fine-tuning docs here.

```python
import asyncio
import os

from lumino.api_sdk.sdk import LuminoSDK


async def main():
    async with LuminoSDK(os.environ.get("LUMSDK_API_KEY")) as client:
        files = await client.dataset.list_datasets()
        await client.dataset.upload_dataset("somefile.jsonl")
        await client.dataset.get_dataset("somefile.jsonl")
        await client.dataset.delete("somefile.jsonl")

        print(files)


asyncio.run(main())
```

### Models
This lists all the models that Lumino supports.

```python
import os
import asyncio
from lumino.api_sdk.sdk import LuminoSDK


async def main():
    async with LuminoSDK(os.environ.get("LUMSDK_API_KEY")) as client:
        models = await client.model.list_base_models()
        print(models)


asyncio.run(main())
```


### Fine-tunes
The finetune API is used for fine-tuning and allows developers to create finetuning jobs. It also has several methods to list all jobs, retrive statuses and get checkpoints. Please refer to our fine-tuning docs here.

```python
import os
import asyncio
from lumino.api_sdk.sdk import LuminoSDK
from lumino.api_sdk.models import FineTuningJobCreate, FineTuningJobParameters


async def main():
    async with LuminoSDK(os.environ.get("LUMSDK_API_KEY")) as client:
        files = await client.dataset.list_datasets()
        job = await client.fine_tuning.create_fine_tuning_job(FineTuningJobCreate(
            base_model_name="llm_llama3_1_8b",
            dataset_name=files[0].name,
            name="test-fine-tuning-job",
            parameters=FineTuningJobParameters(
                batch_size=2,
                shuffle=True,
                num_epochs=1,
                use_lora=True,
                use_qlora=False
            )
        ))

        print(job)

        jobs = await client.fine_tuning.list_fine_tuning_jobs()
        print(jobs)

        job_details = await client.fine_tuning.get_fine_tuning_job(job.name)
        print(job_details)


asyncio.run(main())
```

### Usage Tracking

```python
import os
import asyncio
from lumino.api_sdk.sdk import LuminoSDK
from datetime import timedelta, date


async def main():
    async with LuminoSDK(os.environ.get("LUMSDK_API_KEY")) as client:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        total_cost = await client.usage.get_total_cost(start_date, end_date)
        print(total_cost)

        usage_records = await client.usage.list_usage_records(start_date, end_date)
        print(usage_records)


asyncio.run(main())
```

## Support

If you encounter any problems or have any questions, please open an issue on the GitHub repository.