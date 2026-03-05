# logsentinel-sdk

Python SDK for structured, correlated logging from AWS Lambda functions.

**Status**: In development — see `../docs/v0.2/README.md` for the full specification and task list.

---

## Overview

`logsentinel-sdk` is a lightweight Python library installed inside each Lambda function. It provides:

- `generate_sentinel_id()` — generates a `sent-` prefixed UUID v4 to correlate all events in a single execution
- `Logger` class — batches log events during a Lambda invocation and flushes to Kinesis Data Stream on exit
- Exponential backoff retry on transient Kinesis failures
- Fallback to CloudWatch Logs + SQS DLQ + SNS on persistent failure

## Usage (preview)

```python
from logsentinel import Logger, generate_sentinel_id

def handler(event, context):
    sentinel_id = event.get("sentinel_id") or generate_sentinel_id()
    with Logger(service="battle-service", sentinel_id=sentinel_id) as logger:
        logger.info("Battle started", pokemon="Pikachu", opponent="Mewtwo")
        # pass sentinel_id downstream in the next payload
```

## Configuration

The SDK reads its configuration from SSM Parameter Store at init:

| Parameter | Description |
|-----------|-------------|
| `/logsentinel/stream-name` | Kinesis Data Stream name |
| `/logsentinel/table-name` | DynamoDB table name |
| `/logsentinel/dlq-url` | SQS DLQ URL (fallback) |

These parameters are provisioned automatically by `logsentinel deploy` (in `logsentinel-cli`).

---

For the full specification, architectural decisions, and task list: see `../docs/v0.2/README.md`.
