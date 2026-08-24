from __future__ import annotations

from rest_framework import serializers


class AIQuerySerializer(serializers.Serializer):
    query = serializers.CharField(max_length=500)

    def validate_query(self, value: str) -> str:
        normalized = value.lower()
        forbidden_tokens = ("drop ", "delete ", "truncate ", "alter ", "insert ", "update ")
        if any(token in normalized for token in forbidden_tokens):
            raise serializers.ValidationError("Unsafe query detected. Please use a natural language analytics request.")
        return value.strip()
