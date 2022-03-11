import asyncio
from proxybroker import Broker
import random

async def append(proxies, proxies_list):
    while True:
        proxy = await proxies.get()
        if proxy is None: break
        proxies_list.append(proxy)


def get_proxies():
    proxies_list = []
    proxies = asyncio.Queue()
    broker = Broker(proxies)
    tasks = asyncio.gather(
        broker.find(
            types=['HTTPS'],
            countries=['IT', 'CH', 'NL'],
            limit=10,
            strict=True), append(proxies, proxies_list))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(tasks)
    result = []
    for p in proxies_list:
        p = str(p).split(' ')
        p = p[-1]
        p = p[:-1]
        result.append(p)
    random.shuffle(result)
    return result
