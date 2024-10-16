from pathlib import Path
from extractors.extractor import HttpDriver
from extractors.metro import Extractor
from data_handlers.metro import Handler
from savers import LocalDataSaver

if __name__ == "__main__":
    saver = LocalDataSaver(
        Path("/home/st/projects/testovie/test_MillionAgents/data"),
        "metro",
    )
    ex = Extractor(HttpDriver({}), saver)
    ex.get_list_products()
    ex.extract_data_from_list()

    h = Handler(saver)
    h.clear_data()
