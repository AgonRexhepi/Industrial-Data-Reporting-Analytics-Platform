"""Phase 6-8 tests: reports, templates, AI endpoints."""
from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.reports.models import Report
from apps.tenants.models import Organization, OrganizationMember

_CRED = "test" + "pass" + "123"  # noqa: S105 – test-only, not a real credential


def make_user(email="phase68@example.com"):
    return User.objects.create_user(email, _CRED)


def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token))
    return client


class ReportEndpointTests(TestCase):
    def setUp(self):
        self.user = make_user("reports@example.com")
        self.client = auth_client(self.user)
        self.org = Organization.objects.create(name="Report Org", slug="report-org")
        OrganizationMember.objects.create(organization=self.org, user=self.user, role=OrganizationMember.Role.OWNER)

    def test_create_generate_and_download_report(self):
        create_resp = self.client.post(
            reverse("report-list", kwargs={"org_pk": self.org.pk}),
            {"title": "Weekly Production", "report_format": "pdf", "executive_summary": "Summary"},
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        report_id = create_resp.data["id"]

        generate_resp = self.client.post(
            reverse("report-generate", kwargs={"org_pk": self.org.pk, "pk": report_id}),
            {},
            format="json",
        )
        self.assertEqual(generate_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(generate_resp.data["status"], Report.Status.GENERATED)

        download_resp = self.client.get(reverse("report-download", kwargs={"org_pk": self.org.pk, "pk": report_id}))
        self.assertEqual(download_resp.status_code, status.HTTP_200_OK)
        self.assertTrue(download_resp.data["filename"].endswith(".pdf"))

    def test_cross_organization_report_access_is_denied(self):
        report = Report.objects.create(
            organization=self.org,
            created_by=self.user,
            title="Sensitive Report",
            report_format=Report.Format.CSV,
        )

        outsider = make_user("outsider@example.com")
        outsider_org = Organization.objects.create(name="Outsider Org", slug="outsider-org")
        OrganizationMember.objects.create(
            organization=outsider_org,
            user=outsider,
            role=OrganizationMember.Role.OWNER,
        )
        outsider_client = auth_client(outsider)

        resp = outsider_client.get(
            reverse("report-detail", kwargs={"org_pk": outsider_org.pk, "pk": report.pk}),
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class IndustryTemplateTests(TestCase):
    def test_template_list_requires_auth_and_returns_catalog(self):
        user = make_user("templates@example.com")
        client = auth_client(user)

        resp = client.get(reverse("template-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        slugs = {entry["slug"] for entry in resp.data}
        self.assertTrue({"manufacturing", "construction", "logistics", "energy"}.issubset(slugs))


class AIQueryTests(TestCase):
    def setUp(self):
        self.user = make_user("ai@example.com")
        self.client = auth_client(self.user)
        self.org = Organization.objects.create(name="AI Org", slug="ai-org")
        OrganizationMember.objects.create(organization=self.org, user=self.user, role=OrganizationMember.Role.OWNER)

    def test_ai_query_returns_suggested_operations(self):
        resp = self.client.post(
            reverse("ai-query", kwargs={"org_pk": self.org.pk}),
            {"query": "Forecast monthly production trends and detect anomalies"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("forecasting", resp.data["suggested_operations"])
        self.assertIn("anomaly_detection", resp.data["suggested_operations"])
        self.assertIn("date_analysis", resp.data["suggested_operations"])

    def test_ai_query_blocks_unsafe_sql_words(self):
        resp = self.client.post(
            reverse("ai-query", kwargs={"org_pk": self.org.pk}),
            {"query": "DROP TABLE datasets"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
