import json

from django.test import Client, SimpleTestCase

from game.agent import all_codes_for, game_feedback


class StartEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_start_codebreaker_returns_correct_shape(self):
        resp = self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "codebreaker", "n_colors": 5, "n_pegs": 4, "max_steps": 8}
            ),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["mode"], "codebreaker")
        self.assertEqual(body["n_colors"], 5)
        self.assertEqual(body["n_pegs"], 4)
        self.assertEqual(body["max_steps"], 8)
        self.assertEqual(body["step"], 0)
        self.assertFalse(body["terminated"])
        self.assertFalse(body["truncated"])
        self.assertEqual(body["history"], [])
        self.assertNotIn("secret_idx", body)

    def test_start_codekeeper_returns_ai_guess(self):
        resp = self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "codekeeper", "n_colors": 5, "n_pegs": 4, "max_steps": 8}
            ),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["mode"], "codekeeper")
        self.assertIn("ai_guess_idx", body)
        self.assertIn("ai_guess", body)
        self.assertEqual(len(body["ai_guess"]), 4)
        self.assertIn("consistent_set_size", body)
        self.assertEqual(body["consistent_set_size"], 5**4)
        self.assertNotIn("secret_idx", body)

    def test_start_invalid_n_colors_returns_400(self):
        resp = self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "codebreaker", "n_colors": 2, "n_pegs": 4, "max_steps": 8}
            ),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_start_invalid_max_steps_returns_400(self):
        resp = self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "codebreaker", "n_colors": 5, "n_pegs": 4, "max_steps": 3}
            ),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_start_invalid_mode_returns_400(self):
        resp = self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "invalid", "n_colors": 5, "n_pegs": 4, "max_steps": 8}
            ),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)


class GuessEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "codebreaker", "n_colors": 6, "n_pegs": 4, "max_steps": 8}
            ),
            content_type="application/json",
        )

    def test_guess_returns_feedback(self):
        resp = self.client.post(
            "/api/game/guess/",
            data=json.dumps({"guess_idx": 0}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("blacks", body)
        self.assertIn("whites", body)
        self.assertIn("terminated", body)
        self.assertIn("truncated", body)
        self.assertIn("step", body)
        self.assertEqual(body["step"], 1)
        self.assertNotIn("secret_idx", body)

    def test_guess_correct_feedback_for_known_pair(self):
        all_codes = all_codes_for(6, 4)
        for secret_idx, _ in enumerate(all_codes):
            b, w = game_feedback(all_codes, 0, secret_idx, 6)
            self.assertGreaterEqual(b, 0)
            self.assertGreaterEqual(w, 0)
            self.assertLessEqual(b + w, 4)
        b, w = game_feedback(all_codes, 0, 0, 6)
        self.assertEqual(b, 4)
        self.assertEqual(w, 0)

    def test_guess_increments_step(self):
        self.client.post(
            "/api/game/guess/",
            data=json.dumps({"guess_idx": 0}),
            content_type="application/json",
        )
        resp = self.client.post(
            "/api/game/guess/",
            data=json.dumps({"guess_idx": 1}),
            content_type="application/json",
        )
        self.assertEqual(resp.json()["step"], 2)

    def test_guess_terminated_when_correct(self):
        secret_idx = self.client.session.get("game_state", {}).get("secret_idx")
        if secret_idx is not None:
            resp = self.client.post(
                "/api/game/guess/",
                data=json.dumps({"guess_idx": secret_idx}),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 200)
            self.assertTrue(resp.json()["terminated"])

    def test_guess_invalid_idx_returns_400(self):
        resp = self.client.post(
            "/api/game/guess/",
            data=json.dumps({"guess_idx": 99999}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_guess_without_game_returns_400(self):
        fresh = Client(enforce_csrf_checks=False)
        resp = fresh.post(
            "/api/game/guess/",
            data=json.dumps({"guess_idx": 0}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_secret_idx_never_in_response(self):
        resp = self.client.post(
            "/api/game/guess/",
            data=json.dumps({"guess_idx": 0}),
            content_type="application/json",
        )
        self.assertNotIn("secret_idx", resp.json())


class FeedbackEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)
        resp = self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "codekeeper", "n_colors": 5, "n_pegs": 4, "max_steps": 8}
            ),
            content_type="application/json",
        )
        self.start_body = resp.json()

    def test_feedback_updates_consistent_set(self):
        resp = self.client.post(
            "/api/game/feedback/",
            data=json.dumps({"blacks": 0, "whites": 0}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("consistent_set_size", body)
        self.assertLess(body["consistent_set_size"], 5**4)

    def test_feedback_returns_next_ai_guess(self):
        resp = self.client.post(
            "/api/game/feedback/",
            data=json.dumps({"blacks": 0, "whites": 0}),
            content_type="application/json",
        )
        body = resp.json()
        self.assertIn("ai_guess_idx", body)
        self.assertIn("ai_guess", body)
        self.assertEqual(len(body["ai_guess"]), 4)

    def test_feedback_terminated_when_blacks_equals_n_pegs(self):
        resp = self.client.post(
            "/api/game/feedback/",
            data=json.dumps({"blacks": 4, "whites": 0}),
            content_type="application/json",
        )
        body = resp.json()
        self.assertTrue(body["terminated"])
        self.assertNotIn("ai_guess_idx", body)

    def test_feedback_invalid_blacks_whites_sum_returns_400(self):
        resp = self.client.post(
            "/api/game/feedback/",
            data=json.dumps({"blacks": 3, "whites": 3}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_feedback_invalid_blacks_too_large_returns_400(self):
        resp = self.client.post(
            "/api/game/feedback/",
            data=json.dumps({"blacks": 5, "whites": 0}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_feedback_without_game_returns_400(self):
        fresh = Client(enforce_csrf_checks=False)
        resp = fresh.post(
            "/api/game/feedback/",
            data=json.dumps({"blacks": 0, "whites": 0}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_secret_idx_never_in_feedback_response(self):
        resp = self.client.post(
            "/api/game/feedback/",
            data=json.dumps({"blacks": 0, "whites": 0}),
            content_type="application/json",
        )
        self.assertNotIn("secret_idx", resp.json())


class StateEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_state_no_game_returns_404(self):
        resp = self.client.get("/api/game/state/")
        self.assertEqual(resp.status_code, 404)

    def test_state_codebreaker_no_secret_idx(self):
        self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "codebreaker", "n_colors": 5, "n_pegs": 4, "max_steps": 8}
            ),
            content_type="application/json",
        )
        resp = self.client.get("/api/game/state/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertNotIn("secret_idx", body)
        self.assertEqual(body["mode"], "codebreaker")

    def test_state_codekeeper_includes_ai_guess(self):
        self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "codekeeper", "n_colors": 5, "n_pegs": 4, "max_steps": 8}
            ),
            content_type="application/json",
        )
        resp = self.client.get("/api/game/state/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("ai_guess_idx", body)
        self.assertNotIn("consistent_set", body)
        self.assertNotIn("current_ai_guess_idx", body)


class ResetEndpointTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=False)

    def test_reset_clears_session(self):
        self.client.post(
            "/api/game/start/",
            data=json.dumps(
                {"mode": "codebreaker", "n_colors": 5, "n_pegs": 4, "max_steps": 8}
            ),
            content_type="application/json",
        )
        resp = self.client.post("/api/game/reset/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"ok": True})
        resp2 = self.client.get("/api/game/state/")
        self.assertEqual(resp2.status_code, 404)
