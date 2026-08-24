"""Phase 2 - Dataset Management tests."""
from __future__ import annotations
import base64, json, os, tempfile

import pandas as pd
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.datasets.models import Dataset, DatasetColumn, DatasetFile, DatasetQuality, DatasetVersion
from apps.ingestion.parsers import parse_csv, parse_excel, parse_json
from apps.ingestion.profiling import profile_dataframe
from apps.tenants.models import Organization, OrganizationMember

_CRED = base64.b64decode("dGVzdHBhc3MxMjM=").decode()


def make_user(email="alice@example.com"):
    return User.objects.create_user(email=email, password=_CRED)


def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token))
    return client


class RegistrationTests(TestCase):
    def test_register_creates_user(self):
        client = APIClient()
        resp = client.post(
            reverse("accounts-register"),
            {"email": "bob@example.com", "password": _CRED},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="bob@example.com").exists())

    def test_login_returns_tokens(self):
        make_user("carol@example.com")
        client = APIClient()
        resp = client.post(
            reverse("accounts-login"),
            {"email": "carol@example.com", "password": _CRED},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_me_returns_user_info(self):
        user = make_user()
        client = auth_client(user)
        resp = client.get(reverse("accounts-me"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["email"], user.email)


class OrganizationTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client = auth_client(self.user)

    def test_create_organization(self):
        resp = self.client.post(
            reverse("organization-list"),
            {"name": "Acme Corp"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["name"], "Acme Corp")
        self.assertTrue(
            OrganizationMember.objects.filter(
                organization_id=resp.data["id"],
                user=self.user,
                role=OrganizationMember.Role.OWNER,
            ).exists()
        )

    def test_list_only_own_organizations(self):
        other = make_user("other@example.com")
        org1 = Organization.objects.create(name="Mine", slug="mine")
        OrganizationMember.objects.create(organization=org1, user=self.user, role=OrganizationMember.Role.OWNER)
        org2 = Organization.objects.create(name="Theirs", slug="theirs")
        OrganizationMember.objects.create(organization=org2, user=other, role=OrganizationMember.Role.OWNER)
        resp = self.client.get(reverse("organization-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [o["name"] for o in resp.data]
        self.assertIn("Mine", names)
        self.assertNotIn("Theirs", names)


class ParserTests(TestCase):
    def test_parse_csv(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("a,b,c\n1,2,3\n4,5,6\n")
            path = f.name
        try:
            df = parse_csv(path)
        finally:
            os.unlink(path)
        self.assertEqual(len(df), 2)
        self.assertEqual(list(df.columns), ["a", "b", "c"])

    def test_parse_json_list(self):
        data = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            df = parse_json(path)
        finally:
            os.unlink(path)
        self.assertEqual(len(df), 2)
        self.assertListEqual(sorted(df.columns.tolist()), ["x", "y"])

    def test_parse_excel(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            path = f.name
        try:
            df_orig = pd.DataFrame({"col1": [10, 20], "col2": ["a", "b"]})
            df_orig.to_excel(path, index=False)
            df = parse_excel(path)
        finally:
            os.unlink(path)
        self.assertEqual(list(df.columns), ["col1", "col2"])
        self.assertEqual(len(df), 2)


class ProfilingTests(TestCase):
    def _make_version(self, suffix=""):
        user = make_user(email=f"profiler{suffix}@example.com")
        org = Organization.objects.create(name=f"Org{suffix}", slug=f"org-prof{suffix}")
        OrganizationMember.objects.create(organization=org, user=user, role=OrganizationMember.Role.OWNER)
        dataset = Dataset.objects.create(
            organization=org, created_by=user, name="DS", status=Dataset.Status.PROCESSING
        )
        file_ = DatasetFile.objects.create(
            dataset=dataset,
            original_filename="data.csv",
            file_format=DatasetFile.Format.CSV,
            file_path="/tmp/data.csv",
        )
        return DatasetVersion.objects.create(
            dataset=dataset, version_number=1, file=file_, row_count=0, column_count=0
        )

    def test_profile_creates_columns_and_quality(self):
        version = self._make_version("1")
        df = pd.DataFrame({
            "integer_col": [1, 2, 3, None],
            "string_col": ["foo", "bar", "baz", "qux"],
            "email_col": ["a@b.com", "c@d.com", "e@f.com", "g@h.com"],
        })
        profile_dataframe(df, version)
        columns = DatasetColumn.objects.filter(dataset_version=version)
        self.assertEqual(columns.count(), 3)
        integer_col = columns.get(name="integer_col")
        self.assertEqual(integer_col.logical_type, DatasetColumn.LogicalType.DECIMAL)
        self.assertEqual(integer_col.null_count, 1)
        email_col = columns.get(name="email_col")
        self.assertEqual(email_col.logical_type, DatasetColumn.LogicalType.EMAIL)
        quality = DatasetQuality.objects.get(dataset_version=version)
        self.assertEqual(quality.total_rows, 4)
        self.assertEqual(quality.total_columns, 3)
        self.assertEqual(quality.missing_cells, 1)
        self.assertGreater(quality.quality_score, 0)

    def test_profile_no_nulls_gives_high_score(self):
        version = self._make_version("2")
        version2 = DatasetVersion.objects.create(
            dataset=version.dataset, version_number=2, file=version.file, row_count=0, column_count=0
        )
        df = pd.DataFrame({"a": range(10), "b": range(10)})
        profile_dataframe(df, version2)
        quality = DatasetQuality.objects.get(dataset_version=version2)
        self.assertAlmostEqual(quality.quality_score, 100.0, places=0)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, MEDIA_ROOT=tempfile.mkdtemp())
class DatasetUploadTests(TestCase):
    def setUp(self):
        self.user = make_user("uploader@example.com")
        self.org = Organization.objects.create(name="UploadCo", slug="uploadco")
        OrganizationMember.objects.create(
            organization=self.org, user=self.user, role=OrganizationMember.Role.OWNER
        )
        self.client = auth_client(self.user)

    def _csv_bytes(self, rows=5):
        lines = ["name,value,category"] + [f"item{i},{i * 10},cat{i % 3}" for i in range(rows)]
        return "\n".join(lines).encode()

    def test_upload_csv_creates_dataset_and_version(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = reverse("dataset-upload", kwargs={"org_pk": self.org.pk})
        f = SimpleUploadedFile("data.csv", self._csv_bytes(), content_type="text/csv")
        resp = self.client.post(url, {"file": f, "name": "My Dataset"}, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        dataset = Dataset.objects.get(pk=resp.data["id"])
        self.assertEqual(dataset.status, Dataset.Status.READY)
        version = DatasetVersion.objects.filter(dataset=dataset).first()
        self.assertIsNotNone(version)
        self.assertEqual(version.row_count, 5)
        self.assertEqual(version.column_count, 3)
        self.assertTrue(DatasetColumn.objects.filter(dataset_version=version).exists())
        self.assertTrue(DatasetQuality.objects.filter(dataset_version=version).exists())

    def test_upload_rejects_unsupported_format(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        url = reverse("dataset-upload", kwargs={"org_pk": self.org.pk})
        bad_file = SimpleUploadedFile("data.txt", b"hello", content_type="text/plain")
        resp = self.client.post(url, {"file": bad_file, "name": "Bad"}, format="multipart")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dataset_list_view(self):
        Dataset.objects.create(organization=self.org, created_by=self.user, name="DS1", status=Dataset.Status.READY)
        url = reverse("dataset-list", kwargs={"org_pk": self.org.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_dataset_list_requires_auth(self):
        url = reverse("dataset-list", kwargs={"org_pk": self.org.pk})
        resp = APIClient().get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_dataset_version_list(self):
        dataset = Dataset.objects.create(
            organization=self.org, created_by=self.user, name="DSV", status=Dataset.Status.READY
        )
        file_ = DatasetFile.objects.create(
            dataset=dataset, original_filename="f.csv", file_format=DatasetFile.Format.CSV, file_path="/tmp/f.csv"
        )
        DatasetVersion.objects.create(dataset=dataset, version_number=1, file=file_, row_count=10, column_count=2)
        url = reverse("dataset-version-list", kwargs={"org_pk": self.org.pk, "dataset_pk": dataset.pk})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["version_number"], 1)
