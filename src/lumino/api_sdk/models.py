from datetime import datetime, timezone, date
from enum import Enum
from functools import partial
from typing import List, Dict, Any, Annotated
from uuid import UUID

from pydantic import BaseModel as _BaseModel, Field, EmailStr, PlainSerializer, ConfigDict, field_validator

from lumino.api_sdk.exceptions import LuminoClientError


class UserStatus(str, Enum):
    """Enumeration of possible user statuses."""
    ACTIVE = "ACTIVE"  # User account is active and can be used
    INACTIVE = "INACTIVE"  # User account is deactivated and cannot be used


class ApiKeyStatus(str, Enum):
    """Enumeration of possible API key statuses."""
    ACTIVE = "ACTIVE"  # API key is active and can be used for authentication
    EXPIRED = "EXPIRED"  # API key has expired and is no longer valid
    REVOKED = "REVOKED"  # API key has been manually revoked by the user or admin


class DatasetStatus(str, Enum):
    """Enumeration of possible dataset statuses."""
    UPLOADED = "UPLOADED"  # Dataset has been uploaded but not yet validated
    VALIDATED = "VALIDATED"  # Dataset has been validated and is ready for use
    ERROR = "ERROR"  # There was an error processing or validating the dataset
    DELETED = "DELETED"  # Dataset has been marked as deleted


class FineTuningJobStatus(str, Enum):
    """Enumeration of possible fine-tuning job statuses."""
    NEW = "NEW"  # Job has been created but not yet started
    QUEUED = "QUEUED"  # Job is queued and waiting to start
    RUNNING = "RUNNING"  # Job is currently running
    STOPPING = "STOPPING"  # Job is in the process of being stopped
    STOPPED = "STOPPED"  # Job has been stopped by the user or system
    COMPLETED = "COMPLETED"  # Job has completed successfully
    FAILED = "FAILED"  # Job has failed to complete
    DELETED = "DELETED"  # Job has been marked as deleted


class FineTuningJobType(str, Enum):
    """Enumeration of possible fine-tuning job types."""
    FULL = "FULL"  # Full fine-tuning job
    LORA = "LORA"  # Low-resource fine-tuning job
    QLORA = "QLORA"  # Quantized low-resource fine-tuning job


class BaseModelStatus(str, Enum):
    """Enumeration of possible base model statuses."""
    ACTIVE = "ACTIVE"  # Base model is available for use
    INACTIVE = "INACTIVE"  # Base model is deactivated and cannot be used
    DEPRECATED = "DEPRECATED"  # Base model is no longer supported or recommended for use


class UsageUnit(str, Enum):
    """
    Enum for the unit of the available usage units.
    """
    TOKEN = "TOKEN"


class ServiceName(str, Enum):
    """
    Enum for the name of the available services.
    """
    FINE_TUNING_JOB = "FINE_TUNING_JOB"


class BillingTransactionType(str, Enum):
    """
    Enum for the type of billing transaction.
    """
    MANUAL_ADJUSTMENT = "MANUAL_ADJUSTMENT"
    NEW_USER_CREDIT = "NEW_USER_CREDIT"
    FINE_TUNING_JOB = "FINE_TUNING_JOB"
    STRIPE_CHECKOUT = "STRIPE_CHECKOUT"


class FineTunedModelStatus(str, Enum):
    """Enum of possible fine-tuned model statuses."""
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"


class ComputeProvider(str, Enum):
    """Enum of possible compute providers."""
    GCP = "GCP"
    LUM = "LUM"


class BaseModel(_BaseModel):
    """Base model for all models."""

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.model_dump_json(indent=2)


NameField = partial(Field,
                    min_length=1, max_length=255,
                    pattern="^[a-z0-9-]+$")

DateTime = Annotated[
    datetime,
    PlainSerializer(lambda _datetime: _datetime.strftime("%Y-%m-%dT%H:%M:%SZ"), return_type=str),
]


def _expiration_must_be_future(v: datetime) -> datetime:
    if v.astimezone(timezone.utc) <= datetime.now().astimezone(timezone.utc):
        raise LuminoClientError('Expiration date must be in the future')
    return v


class Pagination(BaseModel):
    """Model for pagination information."""
    total_pages: int
    current_page: int
    items_per_page: int


class ListResponse(BaseModel):
    """Model for list response data."""
    data: List[Any]
    pagination: Pagination


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    """
    name: str | None = Field(None, min_length=1, max_length=255, description="The updated name of the user")


class UserResponse(BaseModel):
    """
    Schema for user response data.
    """
    id: UUID = Field(..., description="The unique identifier for the user")
    created_at: DateTime = Field(..., description="The timestamp when the user was created")
    updated_at: DateTime = Field(..., description="The timestamp when the user was last updated")
    status: UserStatus = Field(..., description="The current status of the user")
    name: str = Field(..., description="The name of the user")
    email: EmailStr = Field(..., description="The email address of the user")
    credits_balance: float = Field(..., description="The current credit balance of the user")
    model_config = ConfigDict(from_attributes=True)


class ApiKeyCreate(BaseModel):
    """
    Schema for creating a new API key.
    """
    name: str = NameField(..., description="The name of the API key")
    expires_at: DateTime = Field(..., description="The expiration date and time of the API key")

    # noinspection PyMethodParameters
    @field_validator('expires_at')
    def expiration_must_be_future(cls, v: datetime) -> datetime:
        return _expiration_must_be_future(v)


class ApiKeyUpdate(BaseModel):
    """
    Schema for updating an existing API key.
    """
    name: str | None = NameField(None, description="The new name for the API key")
    expires_at: datetime | None = Field(None, description="The new expiration date and time for the API key")

    # noinspection PyMethodParameters
    @field_validator('expires_at')
    def expiration_must_be_future(cls, v: datetime) -> datetime:
        return _expiration_must_be_future(v)


class ApiKeyResponse(BaseModel):
    """
    Schema for API key response data.
    """
    id: UUID = Field(..., description="The unique identifier of the API key")
    created_at: DateTime = Field(..., description="The creation date and time of the API key")
    last_used_at: datetime | None = Field(None, description="The last usage date and time of the API key")
    expires_at: DateTime = Field(..., description="The expiration date and time of the API key")
    status: ApiKeyStatus = Field(..., description="The current status of the API key")
    name: str = Field(..., description="The name of the API key")
    prefix: str = Field(..., description="The prefix of the API key (first few characters)")
    model_config = ConfigDict(from_attributes=True)


class ApiKeyWithSecretResponse(ApiKeyResponse):
    """
    Schema for API key response data including the secret key.
    """
    secret: str = Field(..., description="The full API key secret")
    model_config = ConfigDict(from_attributes=True)


class DatasetCreate(BaseModel):
    """
    Schema for creating a new dataset.
    """
    name: str = NameField(..., description="The name of the dataset")
    description: str | None = Field(None, max_length=1000, description="A description of the dataset")


class DatasetUpdate(BaseModel):
    """
    Schema for updating an existing dataset.
    """
    name: str | None = NameField(None, description="The new name for the dataset")
    description: str | None = Field(None, max_length=1000, description="The new description for the dataset")


class DatasetResponse(BaseModel):
    """
    Schema for dataset response data.
    """
    id: UUID = Field(..., description="The unique identifier of the dataset")
    created_at: DateTime = Field(..., description="The timestamp when the dataset was created")
    updated_at: DateTime = Field(..., description="The timestamp when the dataset was last updated")
    status: DatasetStatus = Field(..., description="The current status of the dataset")
    name: str = Field(..., description="The name of the dataset")
    description: str | None = Field(None, description="The description of the dataset, if any")
    file_name: str = Field(..., description="The name of the stored dataset file")
    file_size: int = Field(..., description="The size of the dataset file in bytes")
    errors: dict | None = Field(None, description="Any errors encountered during dataset processing, if any")
    model_config = ConfigDict(from_attributes=True)


class FineTuningJobParameters(BaseModel):
    """Model for fine-tuning job parameters."""
    batch_size: int = Field(default=2, gt=0, le=8)
    shuffle: bool = Field(default=True)
    num_epochs: int = Field(default=1, gt=0, le=10)
    lr: float = Field(default=3e-4, gt=0, le=1)
    seed: int | None = Field(default=None, ge=0)


class FineTuningJobCreate(BaseModel):
    """
    Schema for creating a new fine-tuning job.
    """
    base_model_name: str = Field(..., description="The name of the base model to use for fine-tuning")
    dataset_name: str = Field(..., description="The name of the dataset to use for fine-tuning")
    name: str = NameField(..., description="The name of the fine-tuning job")
    type: FineTuningJobType = Field(..., description="The type of fine-tuning job to run")
    provider: ComputeProvider = Field(ComputeProvider.GCP, description="The compute provider to use for fine-tuning")
    parameters: FineTuningJobParameters = Field(..., description="The parameters for the fine-tuning job")


class FineTuningJobResponse(BaseModel):
    """
    Schema for fine-tuning job response data.
    """
    id: UUID = Field(..., description="The unique identifier of the fine-tuning job")
    created_at: DateTime = Field(..., description="The creation date and time of the fine-tuning job")
    updated_at: DateTime = Field(..., description="The last update date and time of the fine-tuning job")
    base_model_name: str = Field(..., description="The name of the base model used for fine-tuning")
    dataset_name: str = Field(..., description="The name of the dataset used for fine-tuning")
    status: FineTuningJobStatus = Field(..., description="The current status of the fine-tuning job")
    name: str = Field(..., description="The name of the fine-tuning job")
    type: FineTuningJobType = Field(..., description="The type of fine-tuning job")
    provider: ComputeProvider = Field(..., description="The compute provider used for fine-tuning")
    current_step: int | None = Field(None, description="The current step of the fine-tuning process")
    total_steps: int | None = Field(None, description="The total number of steps in the fine-tuning process")
    current_epoch: int | None = Field(None, description="The current epoch of the fine-tuning process")
    total_epochs: int | None = Field(None, description="The total number of epochs in the fine-tuning process")
    num_tokens: int | None = Field(None, description="The number of tokens processed in the fine-tuning job")
    model_config = ConfigDict(from_attributes=True)


class FineTuningJobDetailResponse(FineTuningJobResponse):
    """
    Schema for detailed fine-tuning job response data, including parameters and metrics.
    """
    parameters: Dict[str, Any] = Field(..., description="The parameters used for the fine-tuning job")
    metrics: Dict[str, Any] | None = Field(None, description="The metrics collected during the fine-tuning process")
    timestamps: Dict[str, Any] | None = Field(None,
                                              description="The timestamps recorded during the fine-tuning process")
    model_config = ConfigDict(from_attributes=True)


class BaseModelResponse(BaseModel):
    """
    Schema for base model response data.
    """
    id: UUID = Field(..., description="The unique identifier of the base model")
    description: str | None = Field(None, description="A description of the base model")
    hf_url: str = Field(..., description="The Hugging Face URL for the model")
    status: BaseModelStatus = Field(..., description="The current status of the base model")
    name: str = Field(..., description="The name of the base model")
    meta: Dict[str, Any] | None = Field(None, description="Additional metadata about the base model")
    model_config = ConfigDict(from_attributes=True)


class FineTunedModelResponse(BaseModel):
    """
    Schema for fine-tuned model response data.
    """
    id: UUID = Field(..., description="The unique identifier of the fine-tuned model")
    created_at: DateTime = Field(..., description="The timestamp when the fine-tuned model was created")
    updated_at: DateTime = Field(..., description="The timestamp when the fine-tuned model was last updated")
    fine_tuning_job_name: str = Field(..., description="The name of the associated fine-tuning job")
    status: FineTunedModelStatus = Field(..., description="The current status of the fine-tuned model")
    name: str = Field(..., description="The name of the fine-tuned model")
    artifacts: Dict[str, Any] | None = Field(None,
                                             description="Additional artifacts associated with the fine-tuned model")
    model_config = ConfigDict(from_attributes=True)


class UsageRecordResponse(BaseModel):
    """
    Schema for usage record response data.
    """
    id: UUID = Field(..., description="The unique identifier of the usage record")
    created_at: DateTime = Field(..., description="The timestamp when the usage record was created")
    service_name: ServiceName = Field(..., description="The name of the service used")
    usage_amount: float = Field(..., description="The amount of usage for the service")
    usage_unit: UsageUnit = Field(..., description="The unit of usage for the service")
    cost: float = Field(..., description="The cost associated with the usage")
    fine_tuning_job_name: str = Field(..., description="The name of the associated fine-tuning job")
    model_config = ConfigDict(from_attributes=True)


class TotalCostResponse(BaseModel):
    """
    Schema for total cost response data.
    """
    start_date: date = Field(..., description="The start date of the period for which the cost is calculated")
    end_date: date = Field(..., description="The end date of the period for which the cost is calculated")
    total_cost: float = Field(..., description="The total cost for the specified period")
    model_config = ConfigDict(from_attributes=True)


class CreditHistoryResponse(BaseModel):
    """
    Schema for credit history response data.
    """
    id: UUID = Field(..., description="The unique identifier for the credit record")
    created_at: DateTime = Field(..., description="The timestamp when the credit record was created")
    credits: float = Field(..., description="The amount of credits added or deducted")
    transaction_id: str = Field(..., description="The transaction ID")
    transaction_type: BillingTransactionType = Field(..., description="The type of transaction")
    model_config = ConfigDict(from_attributes=True)
