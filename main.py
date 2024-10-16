from pathlib import Path
from extractor import HttpDriver
from metro import Extractor
from savers import LocalDataSaver

if __name__ == "__main__":
    saver = LocalDataSaver(
        Path("/home/st/projects/testovie/test_MillionAgents/data"),
        "metro",
    )
    ex = Extractor(HttpDriver({}), saver)
    # ex.get_list_products()
    ex.extract_data_from_list()
