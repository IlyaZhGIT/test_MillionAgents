from savers import DataSaver, FileStage
from logger import log
import pandas as pd


class Handler:
    def __init__(
        self,
        saver: DataSaver,
    ) -> None:
        self.saver: DataSaver = saver
        self.log = log

    def clear_data(self) -> None:
        self.log.info("Начало очистки данных")

        try:
            dirty_data = self.saver.recieve_json_data(FileStage.FINAL)
        except FileNotFoundError as e:
            self.log.warning(e)
            raise e

        dirty_data_df = pd.DataFrame(dirty_data)

        if dirty_data_df.empty:
            raise ValueError("Нет данных для очистки")

        self.log.info(f"Будет обработано {len(dirty_data_df)} объектов")

        cleaned_data_df = pd.DataFrame()

        self.log.info("Начало очистки полей")

        cleaned_data_df["create_date"] = dirty_data_df["create_date"]
        cleaned_data_df["link"] = dirty_data_df["link"]
        cleaned_data_df["id"] = dirty_data_df["id"].apply(self._clear_id)
        cleaned_data_df["name"] = dirty_data_df["name"].apply(self._clear_name)
        cleaned_data_df["regular_price"] = dirty_data_df["regular_price"].apply(
            self._clear_regular_price
        )
        cleaned_data_df["promotional_price"] = dirty_data_df["promotional_price"].apply(
            self._clear_promotional_price
        )
        cleaned_data_df["brand"] = dirty_data_df["brand"].apply(self._clear_brand)

        self.log.info(f"Итого объектов {len(cleaned_data_df)}")

        table = [
            cleaned_data_df.columns.values.tolist()
        ] + cleaned_data_df.values.tolist()

        self.saver.save_to_csv(table)

        self.log.info("Конец очистки данных")

    def _clear_id(self, s: str) -> str:
        if not s or not isinstance(s, str):
            return ""

        return s.replace("Артикул:", "").replace("\n", "").strip()

    def _clear_name(self, s) -> str:
        if not s or not isinstance(s, str):
            return ""

        return s.replace("\n", "").strip()

    def _clear_regular_price(self, s) -> str:
        if not s or not isinstance(s, str):
            return ""

        return s.replace("\xa0", "")

    def _clear_promotional_price(self, s) -> str:
        if not s or not isinstance(s, str):
            return ""

        return s.replace("\xa0", "")

    def _clear_brand(self, s) -> str:
        if not s or not isinstance(s, str):
            return ""

        return s.replace("\n", "").strip()
