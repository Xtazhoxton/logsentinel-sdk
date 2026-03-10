import json
import os
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Self

import boto3

if TYPE_CHECKING:
    from mypy_boto3_kinesis.type_defs import PutRecordsRequestEntryTypeDef


class Logger:
    def __init__(
            self,
            service: str,
            sentinel_id: str,
            parent_service: str | None = None,
            endpoint_url: str | None = None,
    ) -> None:
        ssm_client = boto3.client("ssm", endpoint_url=endpoint_url)
        response = ssm_client.get_parameter(Name="/logsentinel/stream-name")
        self._stream_name = response["Parameter"]["Value"]
        self._lambda_request_id = os.environ.get("AWS_LAMBDA_REQUEST_ID")
        self._service = service
        self._sentinel_id = sentinel_id
        self._parent_service = parent_service
        self._buffer: list[dict[str, Any]] = []
        self._kinesis_client = boto3.client("kinesis", endpoint_url=endpoint_url)


    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.flush()

    def _log(self, level: str, message: str, **metadata: object) -> None:
        record: dict[str, Any] = {
            "sentinel_id" : self._sentinel_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "service": self._service,
        }
        if self._parent_service is not None:
            record["parent_service"] = self._parent_service
        if self._lambda_request_id is not None:
            record["lambda_request_id"] = self._lambda_request_id
        record["metadata"] = metadata
        self._buffer.append(record)


    def debug(self, message: str, **metadata: object) -> None:
        self._log("DEBUG", message, **metadata)

    def info(self, message: str, **metadata: object) -> None:
        self._log("INFO", message, **metadata)

    def warning(self, message: str, **metadata: object) -> None:
        self._log("WARNING", message, **metadata)

    def error(self, message: str, **metadata: object) -> None:
        self._log("ERROR", message, **metadata)

    def critical(self, message: str, **metadata: object) -> None:
        self._log("CRITICAL", message, **metadata)

    def flush(self) -> None:
        if len(self._buffer) == 0:
            return None
        formated_records: list[PutRecordsRequestEntryTypeDef] = [
            {
                "Data": json.dumps(record).encode("utf-8"),
                "PartitionKey": self._sentinel_id
            }
            for record in self._buffer]
        self._kinesis_client.put_records(
            StreamName=self._stream_name,
            Records=formated_records
        )
        self._buffer.clear()