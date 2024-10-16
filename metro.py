from lxml import etree
from io import StringIO

from extractor import HttpDriver
from logger.logger import log


class Extractor:
    _BASE_URL: str = "online.metro-cc.ru"

    def __init__(
        self,
        http_extractor: HttpDriver,
    ) -> None:
        self.url = f"https://{self._BASE_URL}/category/chaj-kofe-kakao/kofe"
        self._http_extractor = http_extractor
        self.log = log

    def get_list_products(self):
        self.log.info("Начало извлечения ссылок для города: ")

        response = self._http_extractor.make_request(
            url=self.url,
        )
        if response is None:
            return None

        tree = etree.parse(StringIO(response.text), etree.HTMLParser())

        products_elements = tree.xpath(
            '//div[@id="products-inner"]//a [@data-qa="product-card-name"]'
        )

        if not products_elements:
            return

        links = [
            f"{self._BASE_URL}{element.get("href")}" for element in products_elements
        ]

        print(l)
