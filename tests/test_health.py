from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_health_endpoint_returns_ok(self):
        response = self.client.get(reverse("health-check"))
        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["checks"], {"database": True, "cache": True})
