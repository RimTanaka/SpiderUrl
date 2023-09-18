import scrapy
from ..items import MyItem
from bs4 import BeautifulSoup
import requests
import csv

class TestTaskSpider(scrapy.Spider):
    name = "test_task"
    domains = []
    block_domains = []
    visited_urls = set()  # Храним посещенные URL-адреса

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        middleware = super(TestTaskSpider, cls).from_crawler(crawler, *args, **kwargs)
        middleware.crawler = crawler

        # Загрузка списка доменов и заблокированных доменов
        with (open('../Get_Url_Task/Get_Url_Tz/domains.txt', 'r') as f1,
              open('../Get_Url_Task/Get_Url_Tz/block_domains.txt', 'r') as bl_f2):
            middleware.domains = f1.readlines()
            middleware.domains = [domain.strip() for domain in middleware.domains if domain.strip()]
            # print(domains)
            middleware.block_domains = bl_f2.readlines()
            middleware.block_domains = [block_domain.strip() for block_domain in middleware.block_domains if block_domain.strip()]
            middleware.domains = [domain for domain in middleware.domains if domain not in middleware.block_domains]

            return middleware


    def start_requests(self):
        for url in self.domains:
            if not url.startswith("http://") and not url.startswith("https://"):
                urls_to_try = ["http://" + url, "https://" + url]
            else:
                urls_to_try = [url]

            for url_to_try in urls_to_try:
                # Проверяем, не посещали ли уже этот URL
                if url_to_try not in self.visited_urls:
                    yield scrapy.Request(url_to_try, callback=self.parse)
                    self.visited_urls.add(url_to_try)  # Добавляем URL в список посещенных

    def is_domain_available(self, domain):
        try:
            response = requests.get(domain)
            return response.status_code == 200
        except requests.RequestException:
            return False

        # Определите метод для сохранения данных в CSV-файл

    def save_to_csv(self, item):
        with open('result.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Title', 'Description', 'Email', 'Phone', 'Address', 'Inn', 'Ogrn']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Если файл пустой, записываем заголовки
            if csvfile.tell() == 0:
                writer.writeheader()

            # Записываем данные из объекта item в CSV
            writer.writerow({
                'Title': item['Title'],
                'Description': item['Description'],
                'Email': item['Email'],
                'Phone': item['Phone'],
                'Address': item['Address'],
                'Inn': item['Inn'],
                'Ogrn': item['Ogrn'],
            })

    def parse(self, response):
        try:
            # Создаем экземпляр объекта MyItem
            item = MyItem()

            # Извлекаем заголовок страницы
            title = response.css('title::text').get()
            if title:
                # Удаляем html теги
                title = BeautifulSoup(title, 'html.parser').get_text()
                # Удаляем лишние \n
                title = title.replace('\n', '')
                # Удаляем лишние пробелы
                item['Title'] = ' '.join(title.split())
            else:
                item['Title'] = "н/д"

            # Извлекаем мета-описание
            description = response.xpath('//meta[@name="description"]/@content').get()
            if description:
                # Удаляем html теги
                description = BeautifulSoup(description, 'html.parser').get_text()
                # Удаляем лишние \n
                description = description.replace('\n', '')
                # Удаляем лишние пробелы
                item['Description'] = ' '.join(description.split())
            else:
                item['Description'] = "н/д"

            # Извлекаем электронную почту
            email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
            email = response.css('header').re_first(email_pattern)
            if email:
                item['Email'] = BeautifulSoup(email, 'html.parser').get_text().replace('\n', '')
            else:
                item['Email'] = "н/д"

            # Извлекаем контактный телефон
            # \+\d{1,2} \d{4} \d{2}-\d{2}-\d{2} - +7 3532 22-22-22
            # \+\d{1,2} \d{2} \d{6}-\d{1} - +7 22 123456-0
            # 8\d{10}|\s?\(\d{3}\)\s?\d{3}-\d{2}-\d{2} - "81234567890" "8(800)123-4567" "8-800-555-55-55" "8 (495) 123-45-67".
            # \b\d{3}-\d{3}-\d{4}\b - "123-456-7890"
            phone_pattern = r'(\+\d{1,2} \d{4} \d{2}-\d{2}-\d{2}|\+\d{1,2} \d{2} \d{6}-\d{1}|8\d{10}|\s?\(\d{3}\)\s?\d{3}-\d{2}-\d{2}|\s?\d{3}-\d{3}-\d{2}-\d{2})|\b\d{3}-\d{3}-\d{4}\b'
            phone = response.css('body').re_first(phone_pattern)
            if phone:
                phone = BeautifulSoup(phone, 'html.parser').get_text()
                phone = phone.replace('\n', '')
                item['Phone'] = ' '.join(phone.split())
            else:
                item['Phone'] = "н/д"

            # Извлекаем почтовый адрес
            address_pattern = r'[А-Яа-я\d\s.,-]+(?:д\.|дом|ул\.|улица|пр\.|проспект|пер\.|переулок|бульвар)[\d\w\s.,-]+'
            address = response.css('body').re_first(address_pattern)
            if address:
                address = address.strip()
                address = BeautifulSoup(address, 'html.parser').get_text()
                address = address.replace('\n', '')
                item['Address'] = ' '.join(address.split())
            else:
                item['Address'] = "н/д"

            # Извлекаем ИНН
            inn_pattern = r'\b\d{10}\b'
            inn = response.css('body::text').re(inn_pattern)
            if inn:
                inn = BeautifulSoup(inn, 'html.parser').get_text()
                inn = inn.replace('\n', '')
                item['Inn'] = ' '.join(inn.split())
            else:
                item['Inn'] = "н/д"

            # Извлекаем ОГРН
            ogrn_pattern = r'\b\d{13}\b'
            orgn = response.css('body::text').re(ogrn_pattern)
            if orgn:
                ogrn = BeautifulSoup(orgn, 'html.parser').get_text()
                ogrn = ogrn.replace('\n', '')
                item['Ogrn'] = ' '.join(ogrn.split())
            else:
                item['Ogrn'] = "н/д"


            self.logger.error('Ошибка при парсинге страницы %s', response.url)
        except Exception as ex:
            self.logger.error('Ошибка: %s', str(ex))

        # Возвращаем объект Item с извлеченными данными
        yield item
        self.save_to_csv(item)