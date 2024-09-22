import aiohttp
import ssl
import re
import asyncio
from urllib.parse import urlparse

class PassiveDNSEnum:
    def __init__(self, domain, session, silent=False, verbose=True):
        self.domain = domain
        self.silent = silent
        self.verbose = verbose
        self.subdomains = []
        self.session = session
        self.base_url = f"https://api.sublist3r.com/search.php?domain={domain}"

    def print_(self, text):
        if not self.silent:
            print(text)

    async def enumerate(self):
        sslcontext = ssl.create_default_context()
        sslcontext.check_hostname = False
        sslcontext.verify_mode = ssl.CERT_NONE  # Отключаем проверку сертификатов
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with self.session.get(self.base_url, ssl=sslcontext) as response:
                    if response.status == 200:
                        resp_text = await response.text()
                        self.extract_domains(resp_text)
                        break
            except aiohttp.ClientConnectorError as e:
                self.print_(f"[!] PassiveDNS connection error: {e}")
            except ssl.SSLError as e:
                self.print_(f"[!] PassiveDNS SSL error: {e}")
            except Exception as e:
                self.print_(f"[!] PassiveDNS error: {e}")
            await asyncio.sleep(2)  # Задержка перед повторной попыткой
        return self.subdomains

    def extract_domains(self, response_text):
        subdomains_data = re.findall(r'"(.*?)"', response_text)
        for subdomain in subdomains_data:
            if subdomain and subdomain not in self.subdomains:
                if self.verbose:
                    self.print_(f"[PassiveDNS] {subdomain}")
                self.subdomains.append(subdomain)
