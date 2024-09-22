import aiohttp
import json

class CensysEnum:
    def __init__(self, domain, censys_api_key, censys_secret, session, silent=False, verbose=True):
        self.domain = domain
        self.censys_api_key = censys_api_key
        self.censys_secret = censys_secret
        self.session = session
        self.silent = silent
        self.verbose = verbose
        self.subdomains = []
        self.base_url = "https://search.censys.io/api/v2/hosts/search?q={domain}"

    def print_(self, text):
        if not self.silent:
            print(text)

    async def enumerate(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {self.censys_api_key}:{self.censys_secret}"
        }
        try:
            url = self.base_url.format(domain=self.domain)
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.extract_domains(data)
        except Exception as e:
            self.print_(f"[!] Censys error: {e}")
        return self.subdomains

    def extract_domains(self, data):
        try:
            for result in data["result"]["hits"]:
                subdomain = result["name"]
                if subdomain and subdomain != self.domain and subdomain not in self.subdomains:
                    if self.verbose:
                        self.print_(f"[Censys] {subdomain}")
                    self.subdomains.append(subdomain)
        except KeyError:
            self.print_("[!] Error parsing Censys response")
