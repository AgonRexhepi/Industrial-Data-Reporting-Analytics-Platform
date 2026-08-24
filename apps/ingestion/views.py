from __future__ import annotations

import os
import uuid

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.datasets.models import Dataset, DatasetFile
from apps.datasets.serializers import DatasetSerializer
from apps.tenants.models import OrganizationMember

from .serializers import ALLOWED_EXTENSIONS, DatasetUploadSerializer
from .tasks import process_dataset_file


def _upload_dir(organization_id: str) -> str:
    base = getattr(settings, "MEDIA_ROOT", "/tmp/uploads")
    upload_dir = os.path.join(base, "organizations", str(organization_id), "datasets")
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


class DatasetUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, org_pk):
        if not OrganizationMember.objects.filter(organization_id=org_pk, user=request.user).exists():
            raise NotFound("Organization not found.")

        serializer = DatasetUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]
        original_name = uploaded_file.name
        ext = os.path.splitext(original_name)[1].lstrip(".").lower()
        file_format = ALLOWED_EXTENSIONS[ext]

        display_name = serializer.validated_data.get("name") or os.path.splitext(original_name)[0]
        description = serializer.validated_data.get("description", "")

        # Persist the uploaded file
        upload_dir = _upload_dir(org_pk)
        stored_filename = f"{uuid.uuid4()}{os.path.splitext(original_name)[1]}"
        stored_path = os.path.join(upload_dir, stored_filename)
        with open(stored_path, "wb") as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        # Create dataset + file records
        dataset = Dataset.objects.create(
            organization_id=org_pk,
            created_by=request.user,
            name=display_name,
            description=description,
            status=Dataset.Status.UPLOADING,
        )
        dataset_file = DatasetFile.objects.create(
            dataset=dataset,
            original_filename=original_name,
            file_format=file_format,
            file_path=stored_path,
            file_size=uploaded_file.size,
        )

        # Kick off async processing
        process_dataset_file.delay(str(dataset.pk), str(dataset_file.pk))

        return Response(DatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)
