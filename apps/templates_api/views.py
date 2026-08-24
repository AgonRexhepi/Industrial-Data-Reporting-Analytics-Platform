from __future__ import annotations

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

INDUSTRY_TEMPLATES = [
    {
        "slug": "manufacturing",
        "name": "Manufacturing",
        "kpis": ["Production", "Target", "Efficiency", "OEE", "Downtime", "Defect Rate", "Waste", "Cost"],
        "dashboards": [
            "Production Overview",
            "Machine Performance",
            "Downtime Analysis",
            "Quality Analysis",
            "Cost Analysis",
            "Employee Performance",
        ],
    },
    {
        "slug": "logistics",
        "name": "Logistics",
        "kpis": [
            "Total Deliveries",
            "On-Time Delivery",
            "Distance",
            "Fuel Consumption",
            "Cost per KM",
            "Vehicle Utilization",
        ],
        "dashboards": ["Delivery Performance", "Fleet Efficiency"],
    },
    {
        "slug": "construction",
        "name": "Construction",
        "kpis": [
            "Budget",
            "Actual Cost",
            "Remaining Budget",
            "Project Progress",
            "Labor Hours",
            "Material Cost",
            "Equipment Cost",
        ],
        "dashboards": ["Project Overview", "Cost Control"],
    },
    {
        "slug": "energy",
        "name": "Energy",
        "kpis": ["Consumption", "Production", "Peak Load", "Efficiency", "Cost", "Self Consumption"],
        "dashboards": ["Consumption Analysis", "Production Monitoring"],
    },
    {"slug": "retail", "name": "Retail", "kpis": [], "dashboards": []},
    {"slug": "hospitality", "name": "Hospitality", "kpis": [], "dashboards": []},
]


class IndustryTemplateListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(INDUSTRY_TEMPLATES)
