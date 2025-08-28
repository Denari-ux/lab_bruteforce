#!/usr/bin/env python3
"""
Simulated Provider (simple)
Run: python simulated_provider.py
Serves /check_code endpoint with simple rate-limiting and a random valid code.
"""
from flask import Flask, request, jsonify
from collections import defaultdict
import time
import random

app = Flask(__name__)

# Código válido (aleatório por execução)
VALID_CODES = {f"{random.randint(100000, 999999)}"}  # 6 dígitos
print("[*] Código válido (para laboratório):", list(VALID_CODES)[0])

# Rate limiting / bloqueio simples por IP
ATTEMPT_WINDOW = 60        # segundos
MAX_ATTEMPTS_WINDOW = 10   # tentativas permitidas por janela
BLOCK_DURATION = 300       # 5 minutos

attempts = defaultdict(list)   # ip -> [timestamp,...]
blocked_until = {}             # ip -> timestamp

@app.route("/check_code", methods=["POST"])
def check_code():
    ip = request.remote_addr
    now = time.time()

    # limpar janelas antigas
    attempts[ip] = [t for t in attempts[ip] if now - t <= ATTEMPT_WINDOW]

    # ver se está bloqueado
    if ip in blocked_until and now < blocked_until[ip]:
        return jsonify({"status": "blocked", "message": "IP temporarily blocked"}), 429

    # checar limite
    if len(attempts[ip]) >= MAX_ATTEMPTS_WINDOW:
        blocked_until[ip] = now + BLOCK_DURATION
        return jsonify({"status": "blocked", "message": "Too many attempts — blocked for 5 minutes"}), 429

    data = request.get_json() or {}
    code = data.get("code")
    attempts[ip].append(now)

    # respostas simuladas
    if not code or not code.isdigit():
        return jsonify({"status": "error", "message": "invalidformat"}), 400

    # simula diferenças nas respostas (válido, inválido, try later)
    if code in VALID_CODES:
        return jsonify({"status": "ok", "message": "valid", "balance": "KZ 1,000.00"}), 200
    else:
        # pequena chance de "backoff" do servidor (simula flapping)
        if random.random() < 0.02:
            return jsonify({"status": "error", "message": "service_unavailable"}), 503
        return jsonify({"status": "fail", "message": "invalid"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
