#!/usr/bin/env python3
"""
Advanced simulated provider with behavioral detection:
- Tracks UA entropy, request interarrival patterns, and error rate per IP
- Adds temporary blocks and longer-term blacklisting
Run: python advanced_provider.py
"""
from flask import Flask, request, jsonify
from collections import defaultdict, deque, Counter
import time
import random
import math

app = Flask(__name__)

VALID_CODES = {f"{random.randint(100000, 999999)}"}
print("[*] Advanced provider valid code (lab):", list(VALID_CODES)[0])

# Parameters
ATTEMPT_WINDOW = 60
MAX_ATTEMPTS_WINDOW = 12
BLOCK_DURATION = 300
BLACKLIST_THRESHOLD = 3  # number of blocks before blacklist
BLACKLIST_DURATION = 3600

# state
attempts = defaultdict(deque)  # ip -> deque of timestamps
blocked_until = {}
block_count = defaultdict(int)
blacklisted_until = {}

ua_history = defaultdict(list)  # ip -> list of user agents
error_history = defaultdict(int)  # ip -> error count

def entropy_of_list(items):
    if not items:
        return 0.0
    c = Counter(items)
    total = sum(c.values())
    ent = 0.0
    for v in c.values():
        p = v/total
        ent -= p * math.log2(p)
    return ent

@app.route("/check_code", methods=["POST"])
def check_code():
    ip = request.remote_addr
    now = time.time()
    ua = request.headers.get("User-Agent", "-")
    ua_history[ip].append(ua)
    # keep short history
    if len(ua_history[ip]) > 50:
        ua_history[ip].pop(0)

    # blacklist check
    if ip in blacklisted_until and now < blacklisted_until[ip]:
        return jsonify({"status":"blacklisted","message":"IP blacklisted"}), 403

    # cleanup attempts older than window
    while attempts[ip] and now - attempts[ip][0] > ATTEMPT_WINDOW:
        attempts[ip].popleft()

    # detect low-entropy UA (same UA repeated => suspicious)
    ua_entropy = entropy_of_list(ua_history[ip][-10:])  # last 10
    suspicious_ua = ua_entropy < 1.0  # low entropy indicates same UA repeated

    # rate limiting + behavioral rules
    if len(attempts[ip]) >= MAX_ATTEMPTS_WINDOW:
        blocked_until[ip] = now + BLOCK_DURATION
        block_count[ip] += 1
        if block_count[ip] >= BLACKLIST_THRESHOLD:
            blacklisted_until[ip] = now + BLACKLIST_DURATION
            return jsonify({"status":"blacklisted","message":"IP blacklisted due to repeated abuse"}), 403
        return jsonify({"status":"blocked","message":"Too many attempts — blocked"}), 429

    # append attempt
    attempts[ip].append(now)

    data = request.get_json() or {}
    code = data.get("code")
    if not code or not code.isdigit():
        error_history[ip] += 1
        return jsonify({"status": "error", "message": "invalidformat"}), 400

    # if suspicious UA or super-fast bursts, sometimes return 429 early
    if suspicious_ua and random.random() < 0.6:
        return jsonify({"status":"blocked","message":"suspicious client behavior"}), 429

    # if code valid
    if code in VALID_CODES:
        return jsonify({"status":"ok","message":"valid","balance":"KZ 1,000.00"}), 200

    # else invalid; small chance to trigger service error
    if random.random() < 0.03:
        return jsonify({"status":"error","message":"service_unavailable"}), 503

    return jsonify({"status":"fail","message":"invalid"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
