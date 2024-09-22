import aiohttp

class ShodanEnum:
    def __init__(self, domain, shodan_api_key, session, silent=False, verbose=True):
        self.domain = domain
        self.shodan_api_key = shodan_api_key
        self.session = session
        self.silent = silent
        self.verbose = verbose
        self.subdomains = []
        self.base_url = f"https://api.shodan.io/shodan/host/search?query=hostname:{domain}&minify=True"

    def print_(self, text):
        if not self.silent:
            print(text)

    async def enumerate(self):
        try:
            url = f"{self.base_url}&key={self.shodan_api_key}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    self.extract_domains(data)
                elif response.status == 401:
                    self.print_("[!] Invalid Shodan API key")
        except Exception as e:
            self.print_(f"[!] Shodan error: {e}")
        return self.subdomains

    def extract_domains(self, data):
        try:
            for match in data["matches"]:
                subdomain = match.get("hostnames", [None])[0]
                if subdomain and subdomain != self.domain and subdomain not in self.subdomains:
                    if self.verbose:
                        self.print_(f"[Shodan] {subdomain}")
                    self.subdomains.append(subdomain)
        except KeyError:
            self.print_("[!] Error parsing Shodan response")
