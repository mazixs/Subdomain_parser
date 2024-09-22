import aiohttp
import ssl
import re
from urllib.parse import urlparse

class ThreatCrowdEnum:
    def __init__(self, domain, session, silent=False, verbose=True):
        self.domain = domain
        self.silent = silent
        self.verbose = verbose
        self.subdomains = []
        self.session = session
        self.base_url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={domain}"

    def print_(self, text):
        if not self.silent:
            print(text)

    async def enumerate(self):
        sslcontext = ssl.create_default_context()
        sslcontext.check_hostname = False
        sslcontext.verify_mode = ssl.CERT_NONE  # Отключаем проверку сертификата

        try:
            async with self.session.get(self.base_url, ssl=sslcontext) as response:
                if response.status == 200:
                    resp_text = await response.text()
                    self.extract_domains(resp_text)
        except Exception as e:
            self.print_(f"[!] ThreatCrowd error: {e}")
        return self.subdomains

    def extract_domains(self, response_text):
        subdomains_data = re.findall(r'"subdomains":\["(.*?)"\]', response_text)
        for subdomain in subdomains_data:
            if subdomain and subdomain not in self.subdomains:
                if self.verbose:
                    self.print_(f"[ThreatCrowd] {subdomain}")
                self.subdomains.append(subdomain)
