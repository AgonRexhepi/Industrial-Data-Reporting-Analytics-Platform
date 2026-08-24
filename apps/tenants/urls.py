from django.urls import path

from .views import OrganizationDetailView, OrganizationListCreateView, OrganizationMemberListView

urlpatterns = [
    path("", OrganizationListCreateView.as_view(), name="organization-list"),
    path("<uuid:pk>/", OrganizationDetailView.as_view(), name="organization-detail"),
    path("<uuid:org_pk>/members/", OrganizationMemberListView.as_view(), name="organization-members"),
]
