"""Testes unitários para os algoritmos de Divisão e Conquista (D&C)."""

import math
import random
import unittest
from algorithms import closest_pair, count_inversions, karatsuba, median_of_medians


class TestCountInversions(unittest.TestCase):
    """Testes para o algoritmo de contagem de inversões via Merge Sort O(n log n)."""

    def test_empty_and_single(self):
        self.assertEqual(count_inversions([]), 0)
        self.assertEqual(count_inversions([42]), 0)

    def test_sorted_array(self):
        self.assertEqual(count_inversions([1, 2, 3, 4, 5]), 0)

    def test_reverse_sorted_array(self):
        arr = [5, 4, 3, 2, 1]
        # Inversões máximas: n * (n - 1) / 2 = 10
        self.assertEqual(count_inversions(arr), 10)

    def test_array_with_duplicates(self):
        self.assertEqual(count_inversions([2, 1, 2, 1]), 3)

    def test_matches_brute_force(self):
        random.seed(42)
        for _ in range(10):
            size = random.randint(5, 40)
            sample = [random.randint(-100, 100) for _ in range(size)]
            # Força bruta O(n^2)
            brute = sum(1 for i in range(size) for j in range(i + 1, size) if sample[i] > sample[j])
            self.assertEqual(count_inversions(sample), brute)

    def test_preserves_original_by_default(self):
        arr = [4, 3, 2, 1]
        copy = list(arr)
        count_inversions(arr)
        self.assertEqual(arr, copy)


class TestKaratsuba(unittest.TestCase):
    """Testes para o algoritmo de multiplicação rápida de Karatsuba O(n^1.585)."""

    def test_single_digits(self):
        self.assertEqual(karatsuba(0, 0), 0)
        self.assertEqual(karatsuba(0, 99), 0)
        self.assertEqual(karatsuba(7, 8), 56)

    def test_negative_numbers(self):
        self.assertEqual(karatsuba(-12, 10), -120)
        self.assertEqual(karatsuba(15, -4), -60)
        self.assertEqual(karatsuba(-25, -25), 625)

    def test_type_error_on_floats(self):
        with self.assertRaises(TypeError):
            karatsuba(12.5, 4)  # type: ignore

    def test_large_integers(self):
        x = 987654321098765432109876543210
        y = 123456789012345678901234567890
        self.assertEqual(karatsuba(x, y), x * y)

    def test_random_numbers(self):
        random.seed(42)
        for _ in range(20):
            x = random.randint(-10**9, 10**9)
            y = random.randint(-10**9, 10**9)
            self.assertEqual(karatsuba(x, y), x * y)


class TestMedianOfMedians(unittest.TestCase):
    """Testes para o algoritmo da Mediana das Medianas (BFPRT) O(n)."""

    def test_empty_list_raises_error(self):
        with self.assertRaises(ValueError):
            median_of_medians([])

    def test_out_of_bounds_k(self):
        with self.assertRaises(IndexError):
            median_of_medians([1, 2, 3], k=5)
        with self.assertRaises(IndexError):
            median_of_medians([1, 2, 3], k=-1)

    def test_small_lists(self):
        self.assertEqual(median_of_medians([10]), 10)
        self.assertEqual(median_of_medians([5, 1, 9], 0), 1)
        self.assertEqual(median_of_medians([5, 1, 9], 1), 5)
        self.assertEqual(median_of_medians([5, 1, 9], 2), 9)

    def test_random_selections(self):
        random.seed(42)
        for _ in range(25):
            size = random.randint(1, 60)
            data = [random.randint(-500, 500) for _ in range(size)]
            k = random.randint(0, size - 1)
            expected = sorted(data)[k]
            actual = median_of_medians(data, k)
            self.assertEqual(actual, expected)


class TestClosestPair(unittest.TestCase):
    """Testes para o algoritmo de Par de Pontos Mais Próximo O(n log n)."""

    def test_less_than_two_points(self):
        with self.assertRaises(ValueError):
            closest_pair([])
        with self.assertRaises(ValueError):
            closest_pair([(1.0, 1.0)])

    def test_two_points(self):
        d, p1, p2 = closest_pair([(0.0, 0.0), (3.0, 4.0)])
        self.assertAlmostEqual(d, 5.0, places=4)
        self.assertCountEqual([p1, p2], [(0.0, 0.0), (3.0, 4.0)])

    def test_three_points(self):
        pts = [(0.0, 0.0), (1.0, 0.0), (10.0, 10.0)]
        d, _, _ = closest_pair(pts)
        self.assertAlmostEqual(d, 1.0, places=4)

    def test_points_sharing_coordinates(self):
        pts = [(2.0, 3.0), (2.0, 8.0), (2.0, 1.0), (2.0, 5.0)]
        d, _, _ = closest_pair(pts)
        self.assertAlmostEqual(d, 2.0, places=4)

    def test_matches_brute_force_on_random_points(self):
        random.seed(42)

        def brute_dist(pts):
            best = float("inf")
            for i in range(len(pts)):
                for j in range(i + 1, len(pts)):
                    dist = math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
                    if dist < best:
                        best = dist
            return best

        for _ in range(15):
            count = random.randint(4, 35)
            pts = [(round(random.uniform(-50, 50), 3), round(random.uniform(-50, 50), 3)) for _ in range(count)]
            d, _, _ = closest_pair(pts)
            expected = brute_dist(pts)
            self.assertAlmostEqual(d, expected, places=5)


if __name__ == "__main__":
    unittest.main()
