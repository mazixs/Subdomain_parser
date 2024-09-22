import aiohttp
import re
from urllib.parse import urlparse

class NetcraftEnum:
    def __init__(self, domain, session, silent=False, verbose=True):
        self.domain = domain
        self.silent = silent
        self.verbose = verbose
        self.subdomains = []
        self.session = session
        self.base_url = f"https://searchdns.netcraft.com/?restriction=site+ends+with&host={domain}"

    def print_(self, text):
        if not self.silent:
            print(text)

    async def enumerate(self):
        try:
            async with self.session.get(self.base_url) as response:
                if response.status == 200:
                    resp_text = await response.text()
                    self.extract_domains(resp_text)
        except Exception as e:
            self.print_(f"[!] Netcraft error: {e}")
        return self.subdomains

    def extract_domains(self, response_text):
        link_regx = re.compile(r'<a.*?href="(.*?)"')
        links = link_regx.findall(response_text)
        for link in links:
            subdomain = urlparse(link).netloc
            if subdomain and subdomain != self.domain and subdomain not in self.subdomains:
                if self.verbose:
                    self.print_(f"[Netcraft] {subdomain}")
                self.subdomains.append(subdomain)
