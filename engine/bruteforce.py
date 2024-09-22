import aiohttp
import asyncio
import dns.resolver
import re
from urllib.parse import urlparse

class BruteForceEnum:
    def __init__(self, domain, session, names_file="names.txt", silent=False, verbose=True):
        self.domain = domain
        self.session = session
        self.silent = silent
        self.verbose = verbose
        self.subdomains = []
        self.names_file = names_file

    def print_(self, text):
        if not self.silent:
            print(text)

    def load_subdomain_names(self):
        """Чтение субдоменов из файла names.txt"""
        try:
            with open(self.names_file, 'r') as f:
                subdomain_names = [line.strip() for line in f if line.strip()]
            return subdomain_names
        except FileNotFoundError:
            self.print_(f"[!] Файл {self.names_file} не найден")
            return []

    def generate_subdomains(self, subdomain_names):
        """Генерация субдоменов для проверки"""
        return [f"{name}.{self.domain}" for name in subdomain_names]

    async def check_subdomain_http(self, subdomain):
        """Проверка субдомена через HTTP запрос"""
        try:
            async with self.session.get(f"http://{subdomain}", timeout=5) as response:
                if response.status == 200:
                    if self.verbose:
                        self.print_(f"[VALID] {subdomain}")
                    return subdomain
        except Exception:
            pass
        return None

    def dns_check_subdomain(self, subdomain):
        """Проверка субдомена через DNS запрос"""
        try:
            result = dns.resolver.resolve(subdomain, 'A')
            if result:
                if self.verbose:
                    self.print_(f"[VALID DNS] {subdomain}")
                return subdomain
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            pass  # Не валидный субдомен или отсутствие ответа
        except Exception as e:
            self.print_(f"[!] DNS error for {subdomain}: {e}")
        return None

    async def enumerate(self):
        """Основной метод для запуска брутфорс проверки"""
        # Шаг 1: Загрузить субдомены из файла
        subdomain_names = self.load_subdomain_names()
        if not subdomain_names:
            self.print_("[!] Нет субдоменов для проверки")
            return []

        # Шаг 2: Сгенерировать субдомены
        subdomains_to_check = self.generate_subdomains(subdomain_names)

        # Шаг 3: Асинхронная проверка HTTP + DNS
        tasks = []
        async with aiohttp.ClientSession() as session:
            for subdomain in subdomains_to_check:
                # Добавляем задачу для проверки через HTTP
                tasks.append(self.check_subdomain_http(subdomain))
                # Проверяем через DNS сразу
                dns_result = self.dns_check_subdomain(subdomain)
                if dns_result:
                    self.subdomains.append(dns_result)

            # Асинхронно собираем все результаты HTTP
            http_results = await asyncio.gather(*tasks)

        # Добавляем валидные HTTP субдомены в общий список
        self.subdomains.extend([res for res in http_results if res])

        return self.subdomains
