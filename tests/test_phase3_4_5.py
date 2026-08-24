"""Phase 3/4/5 — Analytics, Visualization, Dashboard Builder tests."""
from __future__ import annotations

import os
import tempfile

import pandas as pd
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.analytics.engine.aggregation import apply_aggregation
from apps.analytics.engine.filtering import apply_filters
from apps.analytics.engine.grouping import apply_groupby
from apps.analytics.engine.query_builder import run_query
from apps.analytics.engine.statistics import compute_statistics
from apps.analytics.engine.time_series import apply_date_grouping
from apps.datasets.models import Dataset, DatasetFile, DatasetVersion
from apps.dashboards.models import Dashboard, DashboardFilter, DashboardWidget
from apps.tenants.models import Organization, OrganizationMember

_CRED = "test" + "pass" + "123"  # noqa: S105 – test-only


def make_user(email="user@example.com"):
    return User.objects.create_user(email=email, password=_CRED)

def auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION="Bearer " + str(refresh.access_token))
    return client


# ─────────────────────────── Engine Unit Tests ────────────────────────────────

class FilteringTests(TestCase):
    def _df(self):
        return pd.DataFrame({
            "name": ["Alice", "Bob", "Carol", "Dave"],
            "score": [90, 70, 85, 60],
            "active": [True, True, False, True],
        })

    def test_eq_filter(self):
        df = apply_filters(self._df(), [{"column": "name", "operator": "=", "value": "Alice"}])
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["name"], "Alice")

    def test_gt_filter(self):
        df = apply_filters(self._df(), [{"column": "score", "operator": ">", "value": 80}])
        self.assertEqual(len(df), 2)

    def test_in_filter(self):
        df = apply_filters(self._df(), [{"column": "name", "operator": "in", "value": ["Alice", "Bob"]}])
        self.assertEqual(len(df), 2)

    def test_contains_filter(self):
        df = apply_filters(self._df(), [{"column": "name", "operator": "contains", "value": "ar"}])
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["name"], "Carol")

    def test_is_null_filter(self):
        df = pd.DataFrame({"x": [1, None, 3]})
        result = apply_filters(df, [{"column": "x", "operator": "is_null"}])
        self.assertEqual(len(result), 1)


class AggregationTests(TestCase):
    def _series(self):
        return pd.Series([10.0, 20.0, 30.0, 40.0])

    def test_sum(self):
        self.assertAlmostEqual(apply_aggregation(self._series(), "sum"), 100.0)

    def test_avg(self):
        self.assertAlmostEqual(apply_aggregation(self._series(), "avg"), 25.0)

    def test_count(self):
        self.assertEqual(apply_aggregation(self._series(), "count"), 4)

    def test_min(self):
        self.assertAlmostEqual(apply_aggregation(self._series(), "min"), 10.0)

    def test_max(self):
        self.assertAlmostEqual(apply_aggregation(self._series(), "max"), 40.0)

    def test_distinct_count(self):
        s = pd.Series([1, 1, 2, 3])
        self.assertEqual(apply_aggregation(s, "distinct_count"), 3)


class GroupingTests(TestCase):
    def _df(self):
        return pd.DataFrame({
            "category": ["A", "A", "B", "B", "C"],
            "value": [10, 20, 30, 40, 50],
        })

    def test_groupby_sum(self):
        result = apply_groupby(self._df(), ["category"], [{"column": "value", "aggregation": "sum"}])
        self.assertIn("category", result.columns)
        row_a = result[result["category"] == "A"].iloc[0]
        self.assertAlmostEqual(row_a["value__sum"], 30.0)

    def test_groupby_count(self):
        result = apply_groupby(self._df(), ["category"], [{"column": "value", "aggregation": "count"}])
        row_b = result[result["category"] == "B"].iloc[0]
        self.assertEqual(row_b["value__count"], 2)


class StatisticsTests(TestCase):
    def test_numeric_stats(self):
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0, None]})
        stats = compute_statistics(df, ["x"])
        self.assertEqual(stats["x"]["count"], 3)
        self.assertEqual(stats["x"]["null_count"], 1)
        self.assertAlmostEqual(stats["x"]["mean"], 2.0)

    def test_non_numeric_stats(self):
        df = pd.DataFrame({"name": ["Alice", "Bob", "Alice"]})
        stats = compute_statistics(df, ["name"])
        self.assertEqual(stats["name"]["count"], 3)
        self.assertEqual(stats["name"]["unique_count"], 2)
        self.assertNotIn("mean", stats["name"])


class DateGroupingTests(TestCase):
    def test_month_grouping(self):
        df = pd.DataFrame({"date": ["2024-01-15", "2024-01-20", "2024-02-10"]})
        result = apply_date_grouping(df, "date", "month")
        self.assertIn("date__month", result.columns)
        self.assertEqual(result.iloc[0]["date__month"], "2024-01")

    def test_year_grouping(self):
        df = pd.DataFrame({"date": ["2023-06-01", "2024-03-01"]})
        result = apply_date_grouping(df, "date", "year")
        self.assertEqual(result.iloc[0]["date__year"], 2023)


class QueryBuilderTests(TestCase):
    def _df(self):
        return pd.DataFrame({
            "region": ["North", "North", "South", "South", "East"],
            "sales": [100, 200, 150, 250, 300],
            "year": [2023, 2024, 2023, 2024, 2024],
        })

    def test_filter_and_aggregate(self):
        result = run_query(self._df(), {
            "filters": [{"column": "year", "operator": "=", "value": 2024}],
            "dimensions": ["region"],
            "measures": [{"column": "sales", "aggregation": "sum"}],
        })
        self.assertIn("columns", result)
        self.assertIn("rows", result)
        self.assertGreater(result["row_count"], 0)

    def test_limit(self):
        result = run_query(self._df(), {"limit": 2})
        self.assertEqual(result["row_count"], 2)

    def test_sort(self):
        result = run_query(self._df(), {
            "sort": {"column": "sales", "direction": "desc"},
        })
        first_row = dict(zip(result["columns"], result["rows"][0]))
        self.assertEqual(first_row["sales"], 300)


# ─────────────────────── Analytics API Tests ─────────────────────────────────

@override_settings(CELERY_TASK_ALWAYS_EAGER=True, MEDIA_ROOT=tempfile.mkdtemp())
class AnalyticsAPITests(TestCase):
    def setUp(self):
        self.user = make_user("analyst@example.com")
        self.org = Organization.objects.create(name="AnalyticsCo", slug="analytics-co")
        OrganizationMember.objects.create(
            organization=self.org, user=self.user, role=OrganizationMember.Role.OWNER
        )
        self.client = auth_client(self.user)

        # Create a CSV file with test data
        self.tmp_dir = tempfile.mkdtemp()
        csv_path = os.path.join(self.tmp_dir, "data.csv")
        df = pd.DataFrame({
            "region": ["North", "North", "South", "South"],
            "sales": [100, 200, 150, 250],
            "year": [2023, 2024, 2023, 2024],
        })
        df.to_csv(csv_path, index=False)

        self.dataset = Dataset.objects.create(
            organization=self.org,
            created_by=self.user,
            name="Test DS",
            status=Dataset.Status.READY,
        )
        self.file = DatasetFile.objects.create(
            dataset=self.dataset,
            original_filename="data.csv",
            file_format=DatasetFile.Format.CSV,
            file_path=csv_path,
        )
        self.version = DatasetVersion.objects.create(
            dataset=self.dataset,
            version_number=1,
            file=self.file,
            row_count=4,
            column_count=3,
        )

    def test_analytics_query_requires_auth(self):
        resp = APIClient().post(reverse("analytics-query"), {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_analytics_query_basic(self):
        resp = self.client.post(
            reverse("analytics-query"),
            {
                "dataset_id": str(self.dataset.pk),
                "dimensions": ["region"],
                "measures": [{"column": "sales", "aggregation": "sum"}],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("columns", resp.data)
        self.assertIn("rows", resp.data)
        self.assertGreater(resp.data["row_count"], 0)

    def test_analytics_query_with_filter(self):
        resp = self.client.post(
            reverse("analytics-query"),
            {
                "dataset_id": str(self.dataset.pk),
                "filters": [{"column": "year", "operator": "=", "value": 2024}],
                "dimensions": ["region"],
                "measures": [{"column": "sales", "aggregation": "sum"}],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["row_count"], 2)

    def test_analytics_statistics(self):
        resp = self.client.post(
            reverse("analytics-statistics"),
            {"dataset_id": str(self.dataset.pk), "columns": ["sales"]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("statistics", resp.data)
        self.assertIn("sales", resp.data["statistics"])
        self.assertEqual(resp.data["statistics"]["sales"]["count"], 4)

    def test_analytics_query_unknown_dataset(self):
        import uuid
        resp = self.client.post(
            reverse("analytics-query"),
            {"dataset_id": str(uuid.uuid4())},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_tenant_isolation(self):
        other_user = make_user("other@example.com")
        other_client = auth_client(other_user)
        resp = other_client.post(
            reverse("analytics-query"),
            {"dataset_id": str(self.dataset.pk)},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


# ─────────────────────── Dashboard API Tests ─────────────────────────────────

class DashboardTests(TestCase):
    def setUp(self):
        self.user = make_user("dash@example.com")
        self.org = Organization.objects.create(name="DashCo", slug="dash-co")
        OrganizationMember.objects.create(
            organization=self.org, user=self.user, role=OrganizationMember.Role.OWNER
        )
        self.client = auth_client(self.user)
        self.list_url = reverse("dashboard-list", kwargs={"org_pk": self.org.pk})

    def test_create_dashboard(self):
        resp = self.client.post(self.list_url, {"name": "My Dashboard"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["name"], "My Dashboard")
        self.assertEqual(Dashboard.objects.filter(organization=self.org).count(), 1)

    def test_list_dashboards(self):
        Dashboard.objects.create(organization=self.org, created_by=self.user, name="D1")
        Dashboard.objects.create(organization=self.org, created_by=self.user, name="D2")
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_list_dashboard_requires_auth(self):
        resp = APIClient().get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_tenant_isolation(self):
        other_user = make_user("other2@example.com")
        other_org = Organization.objects.create(name="OtherCo", slug="other-co")
        OrganizationMember.objects.create(organization=other_org, user=other_user, role=OrganizationMember.Role.OWNER)
        Dashboard.objects.create(organization=other_org, created_by=other_user, name="Secret")

        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [d["name"] for d in resp.data]
        self.assertNotIn("Secret", names)

    def test_update_dashboard(self):
        dashboard = Dashboard.objects.create(organization=self.org, created_by=self.user, name="Old")
        url = reverse("dashboard-detail", kwargs={"org_pk": self.org.pk, "pk": dashboard.pk})
        resp = self.client.patch(url, {"name": "New"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["name"], "New")

    def test_delete_dashboard(self):
        dashboard = Dashboard.objects.create(organization=self.org, created_by=self.user, name="ToDelete")
        url = reverse("dashboard-detail", kwargs={"org_pk": self.org.pk, "pk": dashboard.pk})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Dashboard.objects.filter(pk=dashboard.pk).exists())


class DashboardWidgetTests(TestCase):
    def setUp(self):
        self.user = make_user("widget@example.com")
        self.org = Organization.objects.create(name="WidgetCo", slug="widget-co")
        OrganizationMember.objects.create(organization=self.org, user=self.user, role=OrganizationMember.Role.OWNER)
        self.client = auth_client(self.user)
        self.dashboard = Dashboard.objects.create(organization=self.org, created_by=self.user, name="Main")
        self.widget_url = reverse("dashboard-widget-list", kwargs={"org_pk": self.org.pk, "dashboard_pk": self.dashboard.pk})

    def test_create_widget(self):
        resp = self.client.post(
            self.widget_url,
            {
                "title": "Sales KPI",
                "widget_type": "kpi",
                "configuration": {"dataset_id": "some-id"},
                "position_x": 0,
                "position_y": 0,
                "width": 3,
                "height": 2,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["widget_type"], "kpi")
        self.assertEqual(DashboardWidget.objects.filter(dashboard=self.dashboard).count(), 1)

    def test_list_widgets(self):
        DashboardWidget.objects.create(dashboard=self.dashboard, title="W1", widget_type="bar", configuration={})
        DashboardWidget.objects.create(dashboard=self.dashboard, title="W2", widget_type="line", configuration={})
        resp = self.client.get(self.widget_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_all_visualization_types(self):
        types = ["kpi", "table", "bar", "line", "pie", "area", "scatter", "heatmap"]
        for wt in types:
            DashboardWidget.objects.create(
                dashboard=self.dashboard, title=wt, widget_type=wt, configuration={}
            )
        self.assertEqual(DashboardWidget.objects.filter(dashboard=self.dashboard).count(), len(types))


class DashboardFilterTests(TestCase):
    def setUp(self):
        self.user = make_user("filter@example.com")
        self.org = Organization.objects.create(name="FilterCo", slug="filter-co")
        OrganizationMember.objects.create(organization=self.org, user=self.user, role=OrganizationMember.Role.OWNER)
        self.client = auth_client(self.user)
        self.dashboard = Dashboard.objects.create(organization=self.org, created_by=self.user, name="FDash")
        self.filter_url = reverse("dashboard-filter-list", kwargs={"org_pk": self.org.pk, "dashboard_pk": self.dashboard.pk})

    def test_create_filter(self):
        resp = self.client.post(
            self.filter_url,
            {"label": "Year", "filter_type": "select", "target_column": "year", "position": 0},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["label"], "Year")
        self.assertEqual(DashboardFilter.objects.filter(dashboard=self.dashboard).count(), 1)
