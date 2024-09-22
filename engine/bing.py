import aiohttp
import re
from urllib.parse import urlparse

class BingEnum:
    def __init__(self, domain, session, silent=False, verbose=True):
        self.domain = domain
        self.session = session
        self.silent = silent
        self.verbose = verbose
        self.subdomains = []
        self.base_url = f"https://www.bing.com/search?q=site:{domain}&count=50"

    def print_(self, text):
        if not self.silent:
            print(text)

    async def enumerate(self):
        try:
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    resp_text = await response.text()
                    self.extract_domains(resp_text)
                else:
                    self.print_(f"[!] BingEnum error: Status {response.status}")
        except Exception as e:
            self.print_(f"[!] BingEnum error: {e}")
        return self.subdomains

    def extract_domains(self, response_text):
        # Проверяем если у нас есть валидный HTML ответ, используем регулярку для извлечения доменов
        link_regx = re.compile(r'<cite.*?>(.*?)<\/cite>', re.IGNORECASE)
        links = link_regx.findall(response_text)

        for link in links:
            # Удаляем все HTML-теги и формируем чистую ссылку
            clean_link = re.sub(r'<.*?>', '', link)
            subdomain = urlparse(clean_link).netloc

            if subdomain and subdomain != self.domain and subdomain not in self.subdomains:
                if self.verbose:
                    self.print_(f"[Bing] {subdomain}")
                self.subdomains.append(subdomain)
