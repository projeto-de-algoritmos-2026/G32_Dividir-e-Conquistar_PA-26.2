"""Os 4 algoritmos de divisão e conquista para o trabalho de Projeto de Algoritmos."""

def count_inversions(arr):
    """Conta inversões com merge sort - O(n log n)."""
    def merge(left, mid, right):
        inv = 0
        i, j = left, mid + 1
        temp = []
        while i <= mid and j <= right:
            if arr[i] <= arr[j]:
                temp.append(arr[i]); i += 1
            else:
                # arr[j] vem antes de todos os restantes da metade esquerda
                inv += mid - i + 1
                temp.append(arr[j]); j += 1
        temp.extend(arr[i:mid + 1])
        temp.extend(arr[j:right + 1])
        arr[left:right + 1] = temp
        return inv

    def sort(l, r):
        if l >= r:
            return 0
        m = (l + r) // 2
        return sort(l, m) + sort(m + 1, r) + merge(l, m, r)

    return sort(0, len(arr) - 1)


def karatsuba(x, y):
    """Multiplicação de inteiros grandes - O(n^1.585). Suporta negativos."""
    if x < 0 or y < 0:
        sx, sy = -1 if x < 0 else 1, -1 if y < 0 else 1
        return sx * sy * karatsuba(abs(x), abs(y))
    if x < 10 or y < 10:
        return x * y

    m = max(len(str(x)), len(str(y))) // 2
    high1, low1 = divmod(x, 10 ** m)
    high2, low2 = divmod(y, 10 ** m)

    z0 = karatsuba(low1, low2)
    z2 = karatsuba(high1, high2)
    z1 = karatsuba(high1 + low1, high2 + low2) - z2 - z0

    return z2 * 10 ** (2 * m) + z1 * 10 ** m + z0


def median_of_medians(arr, k=None):
    """Seleciona o k-ésimo menor elemento com garantia O(n) (Blum-Floyd-Pratt-Rivest-Tarjan)."""
    if k is None:
        k = len(arr) // 2  # mediana
    if not arr:
        raise ValueError("lista vazia")

    if len(arr) <= 5:
        return sorted(arr)[k]

    # 1. divide em grupos de 5 e acha a mediana de cada grupo
    medians = [sorted(arr[i:i + 5])[len(arr[i:i + 5]) // 2]
               for i in range(0, len(arr), 5)]

    # 2. mediana das medianas (recursão)
    pivot = median_of_medians(medians, len(medians) // 2)

    # 3. partição em 3 listas
    lows = [x for x in arr if x < pivot]
    highs = [x for x in arr if x > pivot]
    pivots = [x for x in arr if x == pivot]

    if k < len(lows):
        return median_of_medians(lows, k)
    elif k < len(lows) + len(pivots):
        return pivot
    else:
        return median_of_medians(highs, k - len(lows) - len(pivots))


def closest_pair(points):
    """Par de pontos mais próximo - O(n log n). Verifica até 7 pontos vizinhos na faixa.
    Recebe lista de tuplas (x, y); retorna (distância, p1, p2)."""
    import math

    def dist(p, q):
        return math.hypot(p[0] - q[0], p[1] - q[1])

    def brute(pts):
        best = (float('inf'), None, None)
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                d = dist(pts[i], pts[j])
                if d < best[0]:
                    best = (d, pts[i], pts[j])
        return best

    def rec(px, py):
        n = len(px)
        if n <= 3:
            return brute(px)

        mid = n // 2
        midx = px[mid][0]
        dL = rec(px[:mid], [p for p in py if p[0] < midx] or px[:mid])
        dR = rec(px[mid:], [p for p in py if p[0] >= midx] or px[mid:])
        best = min(dL, dR, key=lambda t: t[0])

        # faixa central: pontos a menos de d do meio, ordenados por y
        d = best[0]
        strip = [p for p in py if abs(p[0] - midx) < d]
        # cada ponto compara com no máximo os 7 próximos em y
        for i in range(len(strip)):
            for j in range(i + 1, min(i + 8, len(strip))):
                if strip[j][1] - strip[i][1] >= d:
                    break
                dd = dist(strip[i], strip[j])
                if dd < best[0]:
                    best = (dd, strip[i], strip[j])
        return best

    pts = sorted(points)
    if len(pts) < 2:
        raise ValueError("mínimo de 2 pontos")
    return rec(pts, sorted(pts, key=lambda p: p[1]))
