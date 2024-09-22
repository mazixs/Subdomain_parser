import aiohttp
import re
from urllib.parse import urlparse

class VirusTotalEnum:
    def __init__(self, domain, session, silent=False, verbose=True):
        self.domain = domain
        self.silent = silent
        self.verbose = verbose
        self.subdomains = []
        self.session = session
        self.base_url = f"https://www.virustotal.com/ui/domains/{domain}/subdomains"

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
            self.print_(f"[!] VirusTotal error: {e}")
        return self.subdomains

    def extract_domains(self, response_text):
        subdomains_data = re.findall(r'"id":"(.*?)"', response_text)
        for subdomain in subdomains_data:
            if subdomain and subdomain not in self.subdomains:
                if self.verbose:
                    self.print_(f"[VirusTotal] {subdomain}")
                self.subdomains.append(subdomain)
