"""Testes de integração das rotas HTTP da API Flask do OmniDivide."""

import unittest
from app import app


class TestOmniDivideAPI(unittest.TestCase):
    """Testa os endpoints JSON e validação de requisições."""

    def setUp(self):
        self.client = app.test_client()

    def test_index_route(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Divis", response.data)

    def test_inversions_api_success(self):
        response = self.client.post("/api/inversions", json={"data": "3, 1, 2"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result"], 2)
        self.assertEqual(payload["sorted"], [1, 2, 3])

    def test_karatsuba_api_success(self):
        response = self.client.post("/api/karatsuba", json={"x": 1234, "y": 5678})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result"], str(1234 * 5678))
        self.assertTrue(payload["correct"])

    def test_median_api_success(self):
        response = self.client.post("/api/median", json={"data": "9, 1, 8, 2, 7", "k": 2})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["result"], 7)

    def test_closest_api_success(self):
        response = self.client.post("/api/closest", json={"data": "0,0 3,4 1,1"})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["correct"])
        self.assertAlmostEqual(payload["result"], 1.4142, places=3)

    def test_radar_generate_and_scan(self):
        gen_res = self.client.post("/api/radar/generate", json={"count": 10})
        self.assertEqual(gen_res.status_code, 200)
        aircraft = gen_res.get_json()["aircraft"]
        self.assertEqual(len(aircraft), 10)

        scan_res = self.client.post("/api/radar/scan", json={"aircraft": aircraft})
        self.assertEqual(scan_res.status_code, 200)
        scan_data = scan_res.get_json()
        self.assertIn("distance_km", scan_data)
        self.assertIn("alert", scan_data)
        self.assertIn("brute_comparisons", scan_data)

    def test_match_catalogs_and_affinity(self):
        cat_res = self.client.get("/api/match/catalogs")
        self.assertEqual(cat_res.status_code, 200)
        catalogs = cat_res.get_json()
        self.assertIn("streaming", catalogs)

        items = [item["id"] for item in catalogs["streaming"]["items"]]
        user_order = list(reversed(items))
        aff_res = self.client.post(
            "/api/match/affinity",
            json={"user_order": user_order, "ref_order": items},
        )
        self.assertEqual(aff_res.status_code, 200)
        aff_data = aff_res.get_json()
        self.assertEqual(aff_data["affinity_pct"], 0.0)
        self.assertEqual(aff_data["inversions"], len(items) * (len(items) - 1) // 2)

    def test_fintech_simulate(self):
        response = self.client.post("/api/fintech/simulate", json={"count": 50, "base_latency": 35.0})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("median", data)
        self.assertIn("p90", data)
        self.assertIn("bins", data)

    def test_crypto_generate_and_sign(self):
        gen_res = self.client.post("/api/crypto/generate_keys", json={"digits": 32})
        self.assertEqual(gen_res.status_code, 200)
        keys = gen_res.get_json()
        self.assertEqual(len(keys["key_x"]), 32)
        self.assertEqual(len(keys["key_y"]), 32)

        sign_res = self.client.post(
            "/api/crypto/benchmark_sign",
            json={"key_x": keys["key_x"], "key_y": keys["key_y"], "payload": "PIX Teste"},
        )
        self.assertEqual(sign_res.status_code, 200)
        sign_data = sign_res.get_json()
        self.assertIn("digital_seal", sign_data)
        self.assertIn("savings_pct", sign_data)

    def test_error_handling(self):
        res = self.client.post("/api/radar/scan", json={"aircraft": []})
        self.assertEqual(res.status_code, 400)

        res2 = self.client.post("/api/inversions", json={})
        self.assertEqual(res2.status_code, 400)


if __name__ == "__main__":
    unittest.main()
