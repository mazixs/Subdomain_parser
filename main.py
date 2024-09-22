import aiohttp
import asyncio
import configparser
from engine import google, yahoo, bing, baidu, netcraft, dnsdumpster, virustotal, threatcrowd, crtsearch, passivedns, shodan, censys, bruteforce

# Чтение файла конфигурации
config = configparser.ConfigParser()
config.read('config.ini')

async def run_engines(domain, session):
    """Запуск движков для поиска субдоменов"""
    engines = []

    # Проверяем, включен ли движок в config.ini и добавляем его в список
    if config.getboolean('engines', 'google', fallback=False):
        engines.append(google.GoogleEnum(domain, session))
    if config.getboolean('engines', 'yahoo', fallback=False):
        engines.append(yahoo.YahooEnum(domain, session))
    if config.getboolean('engines', 'bing', fallback=False):
        engines.append(bing.BingEnum(domain, session))
    if config.getboolean('engines', 'baidu', fallback=False):
        engines.append(baidu.BaiduEnum(domain, session))
    if config.getboolean('engines', 'netcraft', fallback=False):
        engines.append(netcraft.NetcraftEnum(domain, session))
    if config.getboolean('engines', 'dnsdumpster', fallback=False):
        engines.append(dnsdumpster.DNSdumpsterEnum(domain, session))
    if config.getboolean('engines', 'virustotal', fallback=False):
        engines.append(virustotal.VirusTotalEnum(domain, session))
    if config.getboolean('engines', 'threatcrowd', fallback=False):
        engines.append(threatcrowd.ThreatCrowdEnum(domain, session))
    if config.getboolean('engines', 'crtsearch', fallback=False):
        engines.append(crtsearch.CrtSearchEnum(domain, session))
    if config.getboolean('engines', 'passivedns', fallback=False):
        engines.append(passivedns.PassiveDNSEnum(domain, session))
    if config.getboolean('engines', 'shodan', fallback=False):
        api_key = config.get('api_keys', 'shodan_api_key', fallback=None)
        if api_key:
            engines.append(shodan.ShodanEnum(domain, session, api_key))
    if config.getboolean('engines', 'censys', fallback=False):
        api_id = config.get('api_keys', 'censys_api_id', fallback=None)
        api_secret = config.get('api_keys', 'censys_api_secret', fallback=None)
        if api_id and api_secret:
            engines.append(censys.CensysEnum(domain, session, api_id, api_secret))
    if config.getboolean('engines', 'bruteforce', fallback=True):  # Включаем брутфорс по умолчанию
        engines.append(bruteforce.BruteForceEnum(domain, session, 'names.txt'))

    subdomains = []

    # Запускаем все движки асинхронно
    tasks = [engine.enumerate() for engine in engines]
    results = await asyncio.gather(*tasks)

    # Собираем результаты всех движков
    for result in results:
        subdomains.extend(result)

    # Убираем дубликаты субдоменов
    subdomains = list(set(subdomains))

    return subdomains

async def main():
    # Ввод домена для поиска субдоменов
    domain = input("Enter domain to search subdomains: ")

    # Чтение настроек вывода и отладки
    output_file = config.get('output', 'output_file', fallback=None)
    debug_mode = config.getboolean('output', 'debug', fallback=False)

    if debug_mode:
        import logging
        logging.basicConfig(level=logging.DEBUG)

    # Асинхронная работа с сессией
    async with aiohttp.ClientSession() as session:
        subdomains = await run_engines(domain, session)

        # Вывод субдоменов в консоль
        print(f"Found {len(subdomains)} subdomains:")
        for subdomain in subdomains:
            print(subdomain)

        # Сохранение результатов в файл, если указано
        if output_file:
            with open(output_file, 'w') as f:
                for subdomain in subdomains:
                    f.write(f"{subdomain}\n")
            print(f"Results saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
