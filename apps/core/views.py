from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        checks = {
            "database": self._database_ok(),
            "cache": self._cache_ok(),
        }
        http_status = status.HTTP_200_OK if all(checks.values()) else status.HTTP_503_SERVICE_UNAVAILABLE
        return Response(
            {
                "status": "ok" if http_status == status.HTTP_200_OK else "degraded",
                "checks": checks,
                "timestamp": timezone.now(),
            },
            status=http_status,
        )

    @staticmethod
    def _database_ok():
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception:
            return False
        return True

    @staticmethod
    def _cache_ok():
        try:
            cache.set("healthcheck", "ok", timeout=5)
            return cache.get("healthcheck") == "ok"
        except Exception:
            return False
