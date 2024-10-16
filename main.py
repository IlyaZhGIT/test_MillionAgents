from extractor import HttpDriver
from metro import Extractor

if __name__ == "__main__":
    ex = Extractor(HttpDriver({}))
    ex.get_list_products()
