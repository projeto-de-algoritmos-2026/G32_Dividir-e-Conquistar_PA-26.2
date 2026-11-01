"""Servidor Flask para o OmniDivide: Suíte de Aplicações de Negócio com Divisão e Conquista."""

import hashlib
import math
import random
import time
import traceback

from flask import Flask, jsonify, render_template, request

from algorithms import closest_pair, count_inversions, karatsuba, median_of_medians

app = Flask(__name__)


def parse_ints(text):
    """Converte "1, 2, 3" em [1, 2, 3]."""
    return [int(x) for x in text.replace(";", ",").split(",") if x.strip()]


def parse_points(text):
    """Converte "x1,y1 x2,y2 ..." ou "x1,y1;x2,y2;..." em [(x1,y1),...]."""
    pts = []
    for pair in text.replace(";", " ").split():
        if not pair.strip():
            continue
        xs, ys = pair.split(",")
        pts.append((float(xs), float(ys)))
    return pts


def timed(fn, *args):
    """Mede tempo de execução com precisão de microsegundos."""
    t0 = time.perf_counter()
    result = fn(*args)
    ms = round((time.perf_counter() - t0) * 1000, 4)
    return result, ms


# -------------------------------------------------------------
# ROTAS PRINCIPAIS E LEGADAS (LABORATÓRIO)
# -------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/api/inversions", methods=["POST"])
def inversions():
    payload = request.get_json(silent=True) or {}
    if "data" not in payload:
        return jsonify({"error": "Parâmetro 'data' obrigatório"}), 400
    data = parse_ints(payload["data"])
    arr = list(data)
    result, ms = timed(count_inversions, arr)
    return jsonify({"result": result, "sorted": sorted(data), "ms": ms, "n": len(data)})


@app.route("/api/karatsuba", methods=["POST"])
def karatsuba_route():
    payload = request.get_json(silent=True) or {}
    if "x" not in payload or "y" not in payload:
        return jsonify({"error": "Parâmetros 'x' e 'y' obrigatórios"}), 400
    try:
        x = int(payload["x"])
        y = int(payload["y"])
    except ValueError:
        return jsonify({"error": "Valores devem ser inteiros válidos"}), 400
    result, ms = timed(karatsuba, x, y)
    correct = result == x * y
    return jsonify({"result": str(result), "correct": correct, "digits": len(str(abs(result))), "ms": ms})


@app.route("/api/median", methods=["POST"])
def median():
    payload = request.get_json(silent=True) or {}
    if "data" not in payload:
        return jsonify({"error": "Parâmetro 'data' obrigatório"}), 400
    data = parse_ints(payload["data"])
    if not data:
        return jsonify({"error": "Lista de números não pode ser vazia"}), 400
    k = payload.get("k")
    if k is None or k == "":
        k = len(data) // 2
    else:
        try:
            k = int(k)
        except ValueError:
            return jsonify({"error": "Parâmetro 'k' deve ser inteiro"}), 400
    k = max(0, min(k, len(data) - 1))
    result, ms = timed(median_of_medians, list(data), k)
    correct = result == sorted(data)[k]
    return jsonify({"result": result, "correct": correct, "sorted": sorted(data), "ms": ms, "n": len(data), "k": k})


@app.route("/api/closest", methods=["POST"])
def closest():
    payload = request.get_json(silent=True) or {}
    if "data" not in payload:
        return jsonify({"error": "Parâmetro 'data' obrigatório"}), 400
    pts = parse_points(payload["data"])
    if len(pts) < 2:
        return jsonify({"error": "Necessário pelo menos 2 pontos"}), 400
    (d, p1, p2), ms = timed(closest_pair, pts)
    best = min(
        ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2, a, b)
        for i, a in enumerate(pts)
        for b in pts[i + 1:]
    )
    correct = abs(d - best[0] ** 0.5) < 1e-7
    return jsonify({
        "result": round(d, 4),
        "p1": [round(p1[0], 2), round(p1[1], 2)],
        "p2": [round(p2[0], 2), round(p2[1], 2)],
        "correct": correct,
        "ms": ms,
        "n": len(pts),
    })


@app.route("/api/random", methods=["POST"])
def random_data():
    payload = request.get_json(silent=True) or {}
    kind = payload.get("kind")
    if kind == "inversions":
        data = [random.randint(0, 999) for _ in range(50)]
        return jsonify({"data": ", ".join(map(str, data))})
    if kind == "median":
        data = [random.randint(0, 999) for _ in range(31)]
        return jsonify({"data": ", ".join(map(str, data))})
    if kind == "closest":
        pts = [(round(random.uniform(0, 100), 2), round(random.uniform(0, 100), 2)) for _ in range(30)]
        return jsonify({"data": " ".join(f"{x},{y}" for x, y in pts)})
    return jsonify({"error": "tipo inválido"}), 400


# -------------------------------------------------------------
# MÓDULO 1: RADAR & DETECÇÃO DE COLISÃO DE AERONAVES (CLOSEST PAIR)
# -------------------------------------------------------------

CALLSIGN_PREFIXES = ["GLO", "TAM", "AZU", "DRN", "FAB", "AMZ", "FDX", "UPS", "ARG", "EZY"]


@app.route("/api/radar/generate", methods=["POST"])
def radar_generate():
    """Gera frota aérea distribuída em um raio geográfico de 100km."""
    count = int(request.json.get("count", 30))
    count = max(2, min(count, 300))
    drones = []
    for i in range(count):
        prefix = random.choice(CALLSIGN_PREFIXES)
        num = random.randint(100, 999)
        callsign = f"{prefix}-{num}"
        # Coordenadas em radar circular de raio ~100
        angle = random.uniform(0, 2 * math.pi)
        r = math.sqrt(random.uniform(0.04, 0.95)) * 100  # distribuição uniforme em disco
        x = round(r * math.cos(angle), 2)
        y = round(r * math.sin(angle), 2)
        # Velocidades pequenas para animação (km/min)
        vx = round(random.uniform(-1.5, 1.5), 2)
        vy = round(random.uniform(-1.5, 1.5), 2)
        altitude = random.randint(1500, 36000)
        drones.append({
            "id": f"ac_{i+1}",
            "callsign": callsign,
            "x": x,
            "y": y,
            "vx": vx,
            "vy": vy,
            "altitude": altitude,
        })
    return jsonify({"aircraft": drones})


@app.route("/api/radar/scan", methods=["POST"])
def radar_scan():
    """Executa detecção de par mais próximo no radar em O(n log n)."""
    payload = request.get_json(silent=True) or {}
    aircraft = payload.get("aircraft", [])
    if len(aircraft) < 2:
        return jsonify({"error": "Necessário no mínimo 2 aeronaves no espaço aéreo"}), 400

    try:
        pts = [(float(a["x"]), float(a["y"])) for a in aircraft]
    except (KeyError, ValueError, TypeError):
        return jsonify({"error": "Formato de coordenadas de aeronave inválido"}), 400

    (d, p1, p2), ms = timed(closest_pair, pts)

    # Identifica quais aeronaves correspondem aos pontos p1 e p2
    ac1 = None
    ac2 = None
    for a in aircraft:
        ax, ay = float(a["x"]), float(a["y"])
        if ac1 is None and abs(ax - p1[0]) < 1e-4 and abs(ay - p1[1]) < 1e-4:
            ac1 = a
        elif ac2 is None and abs(ax - p2[0]) < 1e-4 and abs(ay - p2[1]) < 1e-4:
            ac2 = a

    # Nível de risco de colisão (TCAS)
    if d < 4.0:
        alert = "CRITICAL"
        alert_desc = "🚨 RISCO IMINENTE DE COLISÃO (TCAS RA)"
    elif d < 10.0:
        alert = "WARNING"
        alert_desc = "⚠️ ALERTA DE PROXIMIDADE (TCAS TA)"
    else:
        alert = "SAFE"
        alert_desc = "✅ TRÁFEGO SEGURO"

    # Comparativo com força bruta n*(n-1)/2 vs D&C n*log2(n)
    n = len(aircraft)
    brute_comparisons = n * (n - 1) // 2
    d_and_c_approx = int(n * math.log2(max(2, n)))

    # Ponto de corte da Divisão e Conquista
    pts_sorted_x = sorted(pts, key=lambda p: p[0])
    mid_x = pts_sorted_x[len(pts_sorted_x) // 2][0]

    return jsonify({
        "distance_km": round(d, 3),
        "alert": alert,
        "alert_desc": alert_desc,
        "ac1": ac1,
        "ac2": ac2,
        "mid_x": round(mid_x, 2),
        "strip_width": round(d, 3),
        "ms": ms,
        "n": n,
        "brute_comparisons": brute_comparisons,
        "ops_saved_pct": round(max(0, 100 * (1 - (d_and_c_approx / max(1, brute_comparisons)))), 1),
    })


# -------------------------------------------------------------
# MÓDULO 2: RECOM-MATCH AI — AFINIDADE DE GOSTOS (CONTAGEM DE INVERSÕES)
# -------------------------------------------------------------

CATALOGS = {
    "streaming": {
        "title": "🎬 Cinema & Séries de Culto",
        "description": "Rankeie seus filmes e séries favoritos para comparar afinidade com a crítica e amigos.",
        "items": [
            {"id": "int", "title": "Interestelar", "genre": "Sci-Fi", "year": 2014, "icon": "🚀"},
            {"id": "bb", "title": "Breaking Bad", "genre": "Drama / Crime", "year": 2008, "icon": "🧪"},
            {"id": "god", "title": "O Poderoso Chefão", "genre": "Crime / Drama", "year": 1972, "icon": "🌹"},
            {"id": "br", "title": "Blade Runner 2049", "genre": "Cyberpunk", "year": 2017, "icon": "🌆"},
            {"id": "mtx", "title": "Matrix", "genre": "Ficção Científica", "year": 1999, "icon": "💊"},
            {"id": "drk", "title": "Dark", "genre": "Mistério / Temporal", "year": 2017, "icon": "⏳"},
            {"id": "par", "title": "Parasita", "genre": "Suspense / Drama", "year": 2019, "icon": "🎭"},
            {"id": "opp", "title": "Oppenheimer", "genre": "Histórico / Drama", "year": 2023, "icon": "💥"},
        ],
        "default_critic": ["god", "par", "opp", "bb", "br", "mtx", "int", "drk"],
    },
    "games": {
        "title": "🎮 Games Clássicos & GOTY",
        "description": "Compare suas preferências com a nota agregada dos gamers e críticos mundiais.",
        "items": [
            {"id": "tw3", "title": "The Witcher 3: Wild Hunt", "genre": "RPG", "year": 2015, "icon": "🐺"},
            {"id": "er", "title": "Elden Ring", "genre": "Soulslike", "year": 2022, "icon": "💍"},
            {"id": "rdr2", "title": "Red Dead Redemption 2", "genre": "Mundo Aberto", "year": 2018, "icon": "🤠"},
            {"id": "bg3", "title": "Baldur's Gate 3", "genre": "CRPG", "year": 2023, "icon": "🎲"},
            {"id": "hk", "title": "Hollow Knight", "genre": "Metroidvania", "year": 2017, "icon": "🗡️"},
            {"id": "cp77", "title": "Cyberpunk 2077", "genre": "Action RPG", "year": 2020, "icon": "🦾"},
            {"id": "totk", "title": "Zelda: Tears of the Kingdom", "genre": "Aventura", "year": 2023, "icon": "🛡️"},
            {"id": "hl2", "title": "Half-Life 2", "genre": "FPS Sci-Fi", "year": 2004, "icon": "☢️"},
        ],
        "default_critic": ["rdr2", "bg3", "er", "totk", "tw3", "hl2", "hk", "cp77"],
    },
    "tech": {
        "title": "💻 Arquitetura de Software & Tech Stack",
        "description": "Quais são as maiores prioridades da sua engenharia versus as práticas de mercado?",
        "items": [
            {"id": "t1", "title": "Segurança Zero-Trust", "genre": "SecOps", "year": 2025, "icon": "🛡️"},
            {"id": "t2", "title": "Baixíssima Latência (Sub-5ms)", "genre": "Performance", "year": 2025, "icon": "⚡"},
            {"id": "t3", "title": "Clean Code & Arquitetura Limpa", "genre": "Qualidade", "year": 2025, "icon": "✨"},
            {"id": "t4", "title": "Testes Automatizados E2E", "genre": "QA", "year": 2025, "icon": "🧪"},
            {"id": "t5", "title": "Observabilidade & Tracing Distribuído", "genre": "SRE", "year": 2025, "icon": "📈"},
            {"id": "t6", "title": "Pipeline CI/CD com Deploy Instantâneo", "genre": "DevOps", "year": 2025, "icon": "🚀"},
            {"id": "t7", "title": "IA / LLMs Integradas ao Core", "genre": "AI Engine", "year": 2025, "icon": "🧠"},
            {"id": "t8", "title": "Modularidade / Microsserviços Desacoplados", "genre": "Design", "year": 2025, "icon": "🧩"},
        ],
        "default_critic": ["t1", "t2", "t5", "t4", "t6", "t3", "t8", "t7"],
    },
}


@app.route("/api/match/catalogs", methods=["GET"])
def match_catalogs():
    return jsonify(CATALOGS)


@app.route("/api/match/affinity", methods=["POST"])
def match_affinity():
    """Calcula afinidade entre dois rankings usando Contagem de Inversões O(n log n)."""
    payload = request.get_json(silent=True) or {}
    user_order = payload.get("user_order", [])
    ref_order = payload.get("ref_order", [])

    if len(user_order) != len(ref_order) or len(user_order) < 2:
        return jsonify({"error": "Listas de tamanhos incompatíveis ou insuficientes"}), 400

    n = len(user_order)
    max_inversions = n * (n - 1) // 2

    # Mapeia cada elemento da lista de referência para o seu índice de preferência (0, 1, ..., n-1)
    ref_pos = {item_id: idx for idx, item_id in enumerate(ref_order)}

    # Transforma a ordem do usuário em um array de índices
    mapped_array = [ref_pos[item_id] for item_id in user_order if item_id in ref_pos]

    if len(mapped_array) != n:
        return jsonify({"error": "Itens não coincidem entre as listas"}), 400

    # Executa contagem de inversões
    arr_copy = list(mapped_array)
    inversions, ms = timed(count_inversions, arr_copy)

    # Coeficiente de correlação de Kendall Tau normalizado (0 a 100%)
    affinity_pct = round(max(0.0, (1.0 - (inversions / max_inversions)) * 100.0), 1)

    if affinity_pct >= 85:
        verdict = "💎 Alinhamento Quase Perfeito (Gostos Idênticos)"
        color = "#10b981"
    elif affinity_pct >= 60:
        verdict = "🤝 Alta Afinidade Cultural & Técnica"
        color = "#38bdf8"
    elif affinity_pct >= 35:
        verdict = "⚖️ Gostos Diversificados com Visões Opostas em Pontos Críticos"
        color = "#f59e0b"
    else:
        verdict = "⚡ Gostos Diametralmente Opostos (Inversão Quase Total)"
        color = "#f43f5e"

    # Encontra pares conflitantes (inversões explícitas) para visualização
    conflicts = []
    for i in range(len(mapped_array)):
        for j in range(i + 1, len(mapped_array)):
            if mapped_array[i] > mapped_array[j]:
                conflicts.append({
                    "itemA": user_order[i],
                    "itemB": user_order[j],
                    "user_prefers": user_order[i],
                    "ref_prefers": user_order[j],
                })

    return jsonify({
        "inversions": inversions,
        "max_inversions": max_inversions,
        "affinity_pct": affinity_pct,
        "verdict": verdict,
        "color": color,
        "mapped_array": mapped_array,
        "conflicts_sample": conflicts[:10],
        "ms": ms,
        "n": n,
    })


# -------------------------------------------------------------
# MÓDULO 3: FINPULSE SLA — MONITORAMENTO DE LATÊNCIA (MEDIANA DAS MEDIANAS)
# -------------------------------------------------------------

@app.route("/api/fintech/simulate", methods=["POST"])
def fintech_simulate():
    """Gera telemetria de latência de transações PIX/Cartão e calcula percentis robustos em O(n)."""
    payload = request.get_json(silent=True) or {}
    try:
        n = int(payload.get("count", 400))
        base_latency = float(payload.get("base_latency", 42.0))  # ms
        spike_pct = float(payload.get("spike_pct", 10.0))  # % de outliers provocados por ataques
        spike_magnitude = float(payload.get("spike_magnitude", 1500.0))  # ms do pico
    except (ValueError, TypeError):
        return jsonify({"error": "Parâmetros numéricos inválidos"}), 400

    n = max(20, min(n, 5000))

    latencies = []
    spike_count = int(n * (spike_pct / 100.0))
    normal_count = n - spike_count

    # Transações normais (distribuição lognormal/gaussiana realista de rede)
    for _ in range(normal_count):
        val = max(5.0, random.gauss(base_latency, base_latency * 0.25))
        latencies.append(round(val, 2))

    # Transações com picos (DDoS, timeout de provedor terceiro, lentidão de banco)
    for _ in range(spike_count):
        val = random.uniform(spike_magnitude * 0.7, spike_magnitude * 1.4)
        latencies.append(round(val, 2))

    random.shuffle(latencies)

    # 1. Mediana das medianas (P50 - exata)
    k_med = len(latencies) // 2
    median_val, ms_med = timed(median_of_medians, list(latencies), k_med)

    # 2. P90 e P99 com mediana das medianas
    k_p90 = int(len(latencies) * 0.90)
    p90_val, _ = timed(median_of_medians, list(latencies), k_p90)

    k_p99 = min(len(latencies) - 1, int(len(latencies) * 0.99))
    p99_val, _ = timed(median_of_medians, list(latencies), k_p99)

    # Média aritmética e desvio (muito vulneráveis a outliers!)
    mean_val = round(sum(latencies) / len(latencies), 2)
    variance = sum((x - mean_val) ** 2 for x in latencies) / len(latencies)
    std_val = round(math.sqrt(variance), 2)

    # Status de SLA (SLA contratual: Mediana < 80ms e P90 < 200ms)
    sla_passed = median_val <= 80.0 and p90_val <= 250.0

    # Histograma para renderização do gráfico
    # Criar 25 faixas (bins)
    min_l, max_l = min(latencies), max(latencies)
    bin_count = 24
    step = max(1.0, (max_l - min_l) / bin_count)
    bins = [{"min": round(min_l + i * step, 1), "max": round(min_l + (i + 1) * step, 1), "count": 0} for i in range(bin_count)]

    for l in latencies:
        idx = min(bin_count - 1, int((l - min_l) / step))
        bins[idx]["count"] += 1

    return jsonify({
        "n": len(latencies),
        "median": round(median_val, 2),
        "p90": round(p90_val, 2),
        "p99": round(p99_val, 2),
        "mean": mean_val,
        "std": std_val,
        "skew_impact": round(mean_val - median_val, 2),
        "sla_passed": sla_passed,
        "ms": ms_med,
        "bins": bins,
        "spikes_injected": spike_count,
    })


# -------------------------------------------------------------
# MÓDULO 4: QUANTUM-VAULT HSM — CRIPTOGRAFIA & ASSINATURA (KARATSUBA)
# -------------------------------------------------------------

@app.route("/api/crypto/generate_keys", methods=["POST"])
def crypto_generate_keys():
    """Gera números com alta quantidade de dígitos para simular chaves de alta entropia."""
    payload = request.get_json(silent=True) or {}
    try:
        digits = int(payload.get("digits", 64))
    except (ValueError, TypeError):
        digits = 64
    digits = max(16, min(digits, 1024))

    # Gera inteiros gigantes com os primeiros dígitos diferentes de zero
    x_str = str(random.randint(1, 9)) + "".join([str(random.randint(0, 9)) for _ in range(digits - 1)])
    y_str = str(random.randint(1, 9)) + "".join([str(random.randint(0, 9)) for _ in range(digits - 1)])

    return jsonify({"key_x": x_str, "key_y": y_str, "digits": digits})


@app.route("/api/crypto/benchmark_sign", methods=["POST"])
def crypto_benchmark_sign():
    """Executa Karatsuba em O(n^1.585) e assina digitalmente um payload bancário."""
    payload_data = request.get_json(silent=True) or {}
    x_str = str(payload_data.get("key_x", "")).strip()
    y_str = str(payload_data.get("key_y", "")).strip()
    payload = str(payload_data.get("payload", "TRANSFERÊNCIA PIX R$ 150.000,00 - CLIENTE #8921 -> FORNECEDOR #4412"))

    if not x_str or not y_str:
        return jsonify({"error": "Chaves não fornecidas"}), 400

    try:
        x = int(x_str)
        y = int(y_str)
    except ValueError:
        return jsonify({"error": "As chaves devem conter apenas dígitos válidos"}), 400
    n = max(len(x_str), len(y_str))

    # Executa algoritmo de Karatsuba
    product, ms = timed(karatsuba, x, y)

    # Cálculos teóricos de operações
    ops_school = n * n
    ops_karatsuba = int(n ** 1.585) if n > 1 else 1
    savings_pct = round(max(0.0, ((ops_school - ops_karatsuba) / ops_school) * 100), 2)

    # Gera selo digital HMAC / SHA-256 combinando o produto criptográfico e o payload
    combined = f"{payload}|{product % (10**32)}|TIMESTAMP_{int(time.time())}"
    signature = hashlib.sha256(combined.encode("utf-8")).hexdigest()

    # Formata produto truncado para exibição visual elegante
    prod_str = str(product)
    display_product = prod_str if len(prod_str) <= 60 else f"{prod_str[:25]}...{prod_str[-25:]}"

    return jsonify({
        "product_display": display_product,
        "total_digits": len(prod_str),
        "ms": ms,
        "n_digits": n,
        "ops_school": ops_school,
        "ops_karatsuba": ops_karatsuba,
        "savings_pct": savings_pct,
        "digital_seal": signature,
        "payload": payload,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
    })


@app.errorhandler(Exception)
def on_error(e):
    traceback.print_exc()
    return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
