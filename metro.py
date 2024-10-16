from datetime import datetime
import time
from lxml import etree
from io import StringIO

from extractor import HttpDriver
from logger.logger import log
from savers import DataSaver, FileStage


class Extractor:
    _BASE_URL: str = "online.metro-cc.ru"

    def __init__(self, http_extractor: HttpDriver, saver: DataSaver) -> None:
        self.url = f"https://{self._BASE_URL}/category/chaj-kofe-kakao/kofe"
        self._http_extractor = http_extractor
        self.saver: DataSaver = saver
        self.log = log

    def get_list_products(self):
        self.log.info("Начало извлечения ссылок для города: ")

        response = self._http_extractor.make_request(
            url=self.url,
        )
        if response is None:
            return None

        tree = etree.parse(StringIO(response.text), etree.HTMLParser())

        links = []
        first_page = 1
        last_page: int = self._get_last_page_from_pagination(tree) or 1
        self.log.info(f"Количество страниц будет обработано: {last_page}")

        for page in range(first_page, last_page + 1):
            try:
                try:
                    url = f"{self.url}?page={page}"

                    page_links = self._get_links_from_pages(url)

                    if not page_links:
                        self.log.info(
                            "На странице не найдено подходящих элементов", url=url
                        )
                        continue

                    links.extend(page_links)

                except KeyboardInterrupt:
                    links = {"links": list(set(links))}
                    self.saver.save_to_json(links, FileStage.STAGE)
                    self.log.info("Данные сохранены!")
                    raise
            except Exception as e:
                self.log.warning(
                    e,
                    url=self.url,
                    error_message="Не удалось спарсить страницу с ссылками",
                )
                raise e

        links = {"links": list(set(links))}

        self.log.info(f"Найдено продуктов: {len(links['links'])}")

        self.saver.save_to_json(links, FileStage.STAGE)

        self.log.info("Конец извлечения ссылок")

    def _get_last_page_from_pagination(self, tree) -> int | None:
        xpath = '//ul[@class="catalog-paginate v-pagination"]/li[last()-1]/a'
        elements = tree.xpath(xpath)
        try:
            return int(elements[0].text)
        except (TypeError, IndexError):
            return None

    def _get_links_from_pages(self, url: str) -> list[str] | None:
        self.log.info("Сбор ссылок со страницы", url=url)

        time.sleep(1)
        response = self._http_extractor.make_request(
            url=self.url,
        )
        if response is None:
            return None

        tree = etree.parse(StringIO(response.text), etree.HTMLParser())

        products_elements = tree.xpath(
            '//div[@id="products-inner"]//a [@class="product-card-name reset-link catalog-2-level-product-card__name style--catalog-2-level-product-card"]'
        )

        if products_elements is None:
            self.log.warning("Не найдено ни одного элемента", url=url)
            return None

        self.log.info(f"Обнаружено элементов: {len(products_elements)}")

        links = [
            f"https://{self._BASE_URL}{element.get("href")}"
            for element in products_elements
        ]
        self.log.info(f"Собранно ссылок: {len(links)}")

        return links

    def extract_data_from_list(self):
        self.log.info("Начало извлечения данных")

        links = []
        products = []

        links = list(set(self.saver.recieve_json_data(stage=FileStage.STAGE)["links"]))

        trash_links = []

        try:
            for link in links:
                try:
                    data = self._get_data_from_link(link)

                    products.append(data)

                except Exception as e:
                    self.log.warning(
                        e,
                        url=link,
                        error_message="Не удалось извлечь данные со страницы",
                    )
                    trash_links.append(link)
        except KeyboardInterrupt:
            self.saver.save_to_json(trash_links, FileStage.UNPROCESSED)
            self.saver.save_to_json(products, FileStage.FINAL)
            self.log.info("Данные сохранены!")
            raise

        self.saver.save_to_json(trash_links, FileStage.UNPROCESSED)
        self.saver.save_to_json(products, FileStage.FINAL)

        self.log.info("Конец извлечения данных для города")

    def _get_data_from_link(self, link: str) -> dict[str, str]:
        self.log.info("Начало извлечения данных по ссылке", url=link)

        time.sleep(1)
        response = self._http_extractor.make_request(
            url=link,
        )
        if response is None:
            raise PageIsNotFoundError(link)

        tree = etree.parse(StringIO(response.text), etree.HTMLParser())

        products_data = {
            "create_date": datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M:%SZ"),
            "link": link,
            "id": self._get_id(tree),
            "name": self._get_name(tree),
            "regular_price": self._get_regular_price(tree),
            "promotional_price": self._get_promotional_price(tree),
            "brand": self._get_brand(tree),
        }

        self.log.info("Конец извлечения данных по ссылке", url=link)
        return products_data

    def _get_id(self, tree) -> str | None:
        xpath = '//article//p[@class="product-page-content__article"]'
        element = tree.xpath(xpath)
        if element is None:
            return None

        try:
            return element[0].text
        except IndexError:
            return None

    def _get_name(self, tree) -> str | None:
        xpath = '//article//h1[@class="product-page-content__product-name catalog-heading heading__h2"]/span'
        element = tree.xpath(xpath)
        if element is None:
            return None

        try:
            return element[0].text
        except IndexError:
            return None

    def _get_regular_price(self, tree) -> str | None:
        xpath = '//div[@class="product-page-content__column product-page-content__column--right"]//div[@class="product-unit-prices__trigger"]//div[@class="product-unit-prices__old-wrapper"]//span[@class="product-price__sum-rubles"]'
        element = tree.xpath(xpath)
        if element is None:
            return None

        try:
            return element[0].text
        except IndexError:
            return None

    def _get_promotional_price(self, tree) -> str | None:
        xpath = '//div[@class="product-page-content__column product-page-content__column--right"]//div[@class="product-unit-prices__trigger"]//div[@class="product-unit-prices__actual-wrapper"]//span[@class="product-price__sum-rubles"]'
        element = tree.xpath(xpath)
        if element is None:
            return None

        try:
            return element[0].text
        except IndexError:
            return None

    def _get_brand(self, tree) -> str | None:
        xpath = '//ul [@class="product-attributes__list style--product-page-short-list"]//span[contains(text(), "Бренд")]/parent::node()/parent::node()/a'
        element = tree.xpath(xpath)
        if element is None:
            return None

        try:
            return element[0].text
        except IndexError:
            return None


class PageIsNotFoundError(Exception):
    def __init__(self, link: str) -> None:
        self.message = "Страница не найдена: %s" % link
        super().__init__(self.message)
