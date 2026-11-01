"""Os 4 algoritmos de divisão e conquista para o trabalho de Projeto de Algoritmos.

Módulos implementados:
1. count_inversions: Contagem de inversões via Merge Sort (O(n log n))
2. karatsuba: Multiplicação rápida de inteiros grandes (O(n^1.585))
3. median_of_medians: Seleção do k-ésimo menor elemento (O(n) determinístico)
4. closest_pair: Par de pontos mais próximo no plano 2D (O(n log n))
"""

import math
from typing import List, Optional, Sequence, Tuple, Union

Number = Union[int, float]
Point = Tuple[float, float]


def count_inversions(arr: Sequence[Number], in_place: bool = False) -> int:
    """Conta o número de inversões em uma sequência usando Merge Sort modificado.

    Complexidade: O(n log n).

    Args:
        arr: Sequência de números a ser analisada.
        in_place: Se True, ordena a lista original. Se False, cria uma cópia interna.

    Returns:
        int: Total de pares (i, j) tais que i < j e arr[i] > arr[j].
    """
    if len(arr) <= 1:
        return 0

    working_arr: List[Number] = arr if in_place else list(arr)

    def merge(left: int, mid: int, right: int) -> int:
        inv = 0
        i, j = left, mid + 1
        temp: List[Number] = []

        while i <= mid and j <= right:
            if working_arr[i] <= working_arr[j]:
                temp.append(working_arr[i])
                i += 1
            else:
                # O elemento working_arr[j] é menor que todos os restantes da metade esquerda
                inv += mid - i + 1
                temp.append(working_arr[j])
                j += 1

        temp.extend(working_arr[i : mid + 1])
        temp.extend(working_arr[j : right + 1])
        working_arr[left : right + 1] = temp
        return inv

    def sort(l: int, r: int) -> int:
        if l >= r:
            return 0
        m = (l + r) // 2
        return sort(l, m) + sort(m + 1, r) + merge(l, m, r)

    return sort(0, len(working_arr) - 1)


def karatsuba(x: int, y: int) -> int:
    """Multiplicação rápida de números inteiros grandes pelo algoritmo de Karatsuba.

    Complexidade: O(n^1.585), reduzindo 4 multiplicações escolares para 3 multiplicações recursivas.

    Args:
        x: Primeiro número inteiro.
        y: Segundo número inteiro.

    Returns:
        int: O produto exato de x * y.
    """
    if not isinstance(x, int) or not isinstance(y, int):
        raise TypeError("Os operandos de Karatsuba devem ser inteiros.")

    # Tratamento de sinais negativos
    if x < 0 or y < 0:
        sx = -1 if x < 0 else 1
        sy = -1 if y < 0 else 1
        return sx * sy * karatsuba(abs(x), abs(y))

    # Casos base de parada da recursão
    if x < 10 or y < 10:
        return x * y

    # Determina o expoente de corte (metade do tamanho em dígitos)
    m = max(len(str(x)), len(str(y))) // 2
    power = 10 ** m

    high1, low1 = divmod(x, power)
    high2, low2 = divmod(y, power)

    # 3 chamadas recursivas fundamentais de Karatsuba
    z0 = karatsuba(low1, low2)
    z2 = karatsuba(high1, high2)
    z1 = karatsuba(high1 + low1, high2 + low2) - z2 - z0

    return z2 * (10 ** (2 * m)) + z1 * power + z0


def median_of_medians(arr: Sequence[Number], k: Optional[int] = None) -> Number:
    """Seleciona o k-ésimo menor elemento com garantia de tempo estritamente linear O(n).

    Algoritmo BFPRT (Blum, Floyd, Pratt, Rivest, Tarjan).

    Args:
        arr: Sequência de números não vazia.
        k: Índice desejado (0-indexado). Se None, retorna a mediana (len(arr) // 2).

    Returns:
        Number: O k-ésimo menor elemento na coleção.

    Raises:
        ValueError: Se a lista estiver vazia.
        IndexError: Se k estiver fora dos limites [0, len(arr) - 1].
    """
    if not arr:
        raise ValueError("A lista para a Mediana das Medianas não pode ser vazia.")

    if k is None:
        k = len(arr) // 2

    if not (0 <= k < len(arr)):
        raise IndexError(f"Índice k={k} fora dos limites válidos [0, {len(arr) - 1}].")

    # Caso base para listas pequenas
    if len(arr) <= 5:
        return sorted(arr)[k]

    # 1. Divisão: particiona em blocos de até 5 elementos e acha a mediana de cada bloco
    medians: List[Number] = [
        sorted(arr[i : i + 5])[len(arr[i : i + 5]) // 2]
        for i in range(0, len(arr), 5)
    ]

    # 2. Conquista: encontra a mediana das medianas chamando recursivamente a função
    pivot = median_of_medians(medians, len(medians) // 2)

    # 3. Combinação: particiona em 3 listas usando o pivô equilibrado
    lows = [x for x in arr if x < pivot]
    highs = [x for x in arr if x > pivot]
    pivots_count = len(arr) - len(lows) - len(highs)

    if k < len(lows):
        return median_of_medians(lows, k)
    elif k < len(lows) + pivots_count:
        return pivot
    else:
        return median_of_medians(highs, k - len(lows) - pivots_count)


def closest_pair(points: Sequence[Point]) -> Tuple[float, Point, Point]:
    """Encontra o par de pontos mais próximo em um plano 2D em O(n log n).

    Aplica o teorema da faixa central (strip), onde cada ponto na faixa de largura 2d
    precisa ser comparado com no máximo 7 vizinhos ordenados pela coordenada Y.

    Args:
        points: Sequência de tuplas (x, y) com pelo menos 2 pontos.

    Returns:
        Tuple[float, Point, Point]: (distância_mínima, ponto_1, ponto_2).

    Raises:
        ValueError: Se forem fornecidos menos de 2 pontos.
    """
    if len(points) < 2:
        raise ValueError("Necessário no mínimo 2 pontos para calcular o par mais próximo.")

    def dist(p: Point, q: Point) -> float:
        return math.hypot(p[0] - q[0], p[1] - q[1])

    def brute_force(pts: Sequence[Point]) -> Tuple[float, Point, Point]:
        best_d = float("inf")
        p1: Optional[Point] = None
        p2: Optional[Point] = None
        n = len(pts)
        for i in range(n):
            for j in range(i + 1, n):
                d = dist(pts[i], pts[j])
                if d < best_d:
                    best_d = d
                    p1, p2 = pts[i], pts[j]
        return best_d, p1, p2  # type: ignore

    # Cria cópias indexadas para preservar estabilidade mesmo com pontos duplicados
    indexed_points = list(enumerate(points))

    def rec(px_idx: List[Tuple[int, Point]], py_idx: List[Tuple[int, Point]]) -> Tuple[float, Point, Point]:
        n = len(px_idx)
        if n <= 3:
            raw_pts = [pt for _, pt in px_idx]
            return brute_force(raw_pts)

        mid = n // 2
        mid_x = px_idx[mid][1][0]

        left_ids = {idx for idx, _ in px_idx[:mid]}

        py_left = [item for item in py_idx if item[0] in left_ids]
        py_right = [item for item in py_idx if item[0] not in left_ids]

        dl = rec(px_idx[:mid], py_left)
        dr = rec(px_idx[mid:], py_right)
        best = dl if dl[0] < dr[0] else dr
        d = best[0]

        # Faixa central: pontos a uma distância horizontal menor que d da linha de corte
        strip = [pt for _, pt in py_idx if abs(pt[0] - mid_x) < d]
        strip_len = len(strip)

        for i in range(strip_len):
            # No máximo 7 comparações necessárias por causa do empacotamento no retângulo d x 2d
            limit = min(i + 8, strip_len)
            for j in range(i + 1, limit):
                if strip[j][1] - strip[i][1] >= d:
                    break
                dd = dist(strip[i], strip[j])
                if dd < best[0]:
                    best = (dd, strip[i], strip[j])

        return best

    pts_x = sorted(indexed_points, key=lambda item: (item[1][0], item[1][1]))
    pts_y = sorted(indexed_points, key=lambda item: (item[1][1], item[1][0]))

    return rec(pts_x, pts_y)
