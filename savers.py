import csv
from enum import Enum
import json
from pathlib import Path
from typing import Any, Protocol


class FileStage(Enum):
    STAGE = "stage"
    FINAL = "final"
    UNPROCESSED = "unprocessed"


class DataSaver(Protocol):
    def save_to_json(self, data: Any, stage: FileStage) -> None:
        raise NotImplementedError

    def save_to_csv(self, data: Any, fieldnames: list | None = None) -> None:
        raise NotImplementedError

    def recieve_json_data(self, stage: FileStage) -> Any:
        raise NotImplementedError

    def recieve_csv_data(self) -> list:
        raise NotImplementedError


class LocalDataSaver:
    def __init__(self, path: Path, files_unique_id: str) -> None:
        self.path = path
        self.files_unique_id = files_unique_id

    def save_to_json(self, data: Any, stage: FileStage) -> None:
        with open(f"{self.path}/{stage.value}-{self.files_unique_id}.json", "w") as f:
            json.dump(data, f, ensure_ascii=False)

    def save_to_csv(self, data: Any, fieldnames: list | None = None) -> None:
        with open(f"{self.path}/{self.files_unique_id}.csv", "w") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerows(data)

    def recieve_json_data(self, stage: FileStage) -> Any:
        with open(f"{self.path}/{stage.value}-{self.files_unique_id}.json", "r") as f:
            return json.load(f)

    def recieve_csv_data(self) -> list:
        with open(f"{self.path}/{self.files_unique_id}.csv", "r") as f:
            reader = csv.DictReader(f, delimiter=";")
            return list(reader)


class DataSaverMock:
    def save_to_json(self, data: dict) -> None: ...

    def save_to_csv(self, data: dict, fieldnames: list | None = None) -> None: ...

    def recieve_json_data(self) -> dict: ...

    def recieve_csv_data(self) -> list: ...
