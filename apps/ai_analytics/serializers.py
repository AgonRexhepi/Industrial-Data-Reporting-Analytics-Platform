from __future__ import annotations

from rest_framework import serializers


class AIQuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=500)

    def validate_query(self, value: str) -> str:
        normalized = value.lower()
        forbidden_tokens = {"drop", "delete", "truncate", "alter", "insert", "update"}
        words = set(normalized.replace("\n", " ").replace("\t", " ").split())
        if forbidden_tokens.intersection(words):
            raise serializers.ValidationError("Unsafe query detected. Please use a natural language analytics request.")
        return value.strip()
