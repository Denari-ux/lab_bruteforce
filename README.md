# HTB BruteForce Lab 🦅

Laboratório educacional seguro.
Veja HELP.md para detalhes.
🦅🔥 Show! Vamos fechar o pacote bonito: documentação completa, help embutido, instruções de instalação e um repositório GitHub pronto pra você publicar. Vou montar tudo dentro da pasta e te entregar em `.zip`.

---

# Estrutura final do projeto

```
htb_bruteforce_lab/
│
├── simulated_provider.py     # Servidor simples (rate-limiting básico)
├── advanced_provider.py      # Servidor avançado (detecção comportamental)
├── lab_bruteforce.py         # Cliente brute-force simples
├── smart_client.py           # Cliente avançado (jitter, proxy rotation, evasão)
├── requirements.txt          # Dependências
├── run.sh                    # Script de setup rápido
├── README.md                 # Documentação e instruções de uso
└── HELP.md                   # Guia detalhado de help/comandos
```

---

# Conteúdo dos arquivos extras

## `requirements.txt`

```txt
flask
aiohttp
```

## `run.sh`

```bash
#!/bin/bash
set -e

echo "[*] Criando virtualenv..."
python3 -m venv venv
source venv/bin/activate

echo "[*] Instalando dependências..."
pip install -r requirements.txt

echo "[*] Ambiente pronto!"
```

## `README.md`

````markdown
# HTB BruteForce Lab 🦅

Laboratório seguro para treinar técnicas de brute-force contra sistemas de recarga/saldo,
simulando endpoints de uma operadora. **Uso exclusivo em ambiente autorizado (HackTheBox, lab pessoal).**

---

## 🚀 Instalação
Clone o repositório ou descompacte o zip:

```bash
git clone https://github.com/SEU-USUARIO/htb_bruteforce_lab.git
cd htb_bruteforce_lab
````

Crie o ambiente virtual e instale dependências:

```bash
./run.sh
```

---

## ⚡ Uso

### 1. Rodar servidor simulado

Servidor básico (porta 5000):

```bash
python simulated_provider.py
```

Servidor avançado com detecção:

```bash
python advanced_provider.py
```

O servidor imprime o **código válido** no terminal (para teste de brute-force).

---

### 2. Rodar cliente brute-force

Cliente simples:

```bash
python lab_bruteforce.py
```

Cliente avançado (jitter, evasão, proxy rotation fake):

```bash
python smart_client.py
```

---

## 📘 Documentação

Veja [`HELP.md`](HELP.md) para detalhes sobre parâmetros, exemplos e explicação técnica.

---

⚠️ Aviso Legal

Este projeto é **apenas para fins educacionais** em laboratórios controlados.
**Não use contra redes, operadoras ou sistemas reais.** Isso é ilegal.

````

## `HELP.md`
```markdown
# HELP - HTB BruteForce Lab

Este documento detalha como usar os scripts e o que cada um faz.

---

## simulated_provider.py
Servidor básico (Flask).  
- Porta: 5000
- Gera um código válido aleatório (6 dígitos).
- Limite: 10 tentativas/minuto por IP. Excede → bloqueio por 5 min.

Início:
```bash
python simulated_provider.py
````

---

## advanced\_provider.py

Servidor avançado:

* Monitora padrões de user-agent.
* Detecta bursts de requisições.
* Aplica bloqueio comportamental além do rate-limit.

---

## lab\_bruteforce.py

Cliente simples (asyncio + aiohttp).
Parâmetros editáveis no código:

* `CONCURRENCY`: nº de workers.
* `MAX_CODES`: nº de tentativas no lab.
* `START/END`: intervalo de códigos.

Execução:

```bash
python lab_bruteforce.py
```

---

## smart\_client.py

Cliente avançado com:

* Jitter (intervalos variáveis).
* Throttling adaptativo.
* Rotação de “proxies” (simulada).

Execução:

```bash
python smart_client.py
```

## Fluxo recomendado de aprendizado

1. Rodar `simulated_provider.py` + `lab_bruteforce.py` → entender o básico.
2. Trocar para `advanced_provider.py` + `smart_client.py` → estudar evasão.
3. Ajustar parâmetros e observar logs no servidor → análise de detecção.

## Dependências

* Python 3.8+
* Flask
* aiohttp

Instalação:

```bash
pip install -r requirements.txt
```
