from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def process_dataset_file(self, dataset_id: str, file_id: str) -> dict:
    """
    Parse an uploaded file, detect column types, profile the data, and
    calculate data-quality metrics.

    Updates Dataset.status throughout the workflow.
    """
    from apps.datasets.models import Dataset, DatasetFile, DatasetVersion

    from .parsers import parse_file
    from .profiling import profile_dataframe

    try:
        dataset = Dataset.objects.get(pk=dataset_id)
        dataset_file = DatasetFile.objects.get(pk=file_id)

        dataset.status = Dataset.Status.PROCESSING
        dataset.save(update_fields=["status"])

        logger.info("Processing dataset %s — file %s", dataset_id, file_id)

        df = parse_file(dataset_file.file_path, dataset_file.file_format)

        # Create or increment version
        last_version = dataset.versions.order_by("-version_number").first()
        version_number = (last_version.version_number + 1) if last_version else 1

        version = DatasetVersion.objects.create(
            dataset=dataset,
            version_number=version_number,
            file=dataset_file,
            row_count=len(df),
            column_count=len(df.columns),
            created_by=dataset.created_by,
        )

        dataset.status = Dataset.Status.VALIDATING
        dataset.save(update_fields=["status"])

        profile_dataframe(df, version)

        # Update dataset totals from the new version
        dataset.row_count = version.row_count
        dataset.column_count = version.column_count
        dataset.status = Dataset.Status.READY
        dataset.save(update_fields=["row_count", "column_count", "status"])

        logger.info("Dataset %s ready — %s rows, %s cols", dataset_id, version.row_count, version.column_count)

        return {
            "dataset_id": dataset_id,
            "version": version_number,
            "rows": version.row_count,
            "columns": version.column_count,
        }

    except Exception as exc:
        logger.exception("Failed to process dataset %s: %s", dataset_id, exc)
        if self.request.retries >= self.max_retries:
            try:
                Dataset.objects.filter(pk=dataset_id).update(status=Dataset.Status.FAILED)
            except Exception:
                pass
        raise self.retry(exc=exc)
