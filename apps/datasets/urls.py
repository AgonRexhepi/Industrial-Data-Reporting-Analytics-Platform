from django.urls import path

from .views import DatasetDetailView, DatasetListView, DatasetVersionDetailView, DatasetVersionListView

urlpatterns = [
    path("", DatasetListView.as_view(), name="dataset-list"),
    path("<uuid:pk>/", DatasetDetailView.as_view(), name="dataset-detail"),
    path("<uuid:dataset_pk>/versions/", DatasetVersionListView.as_view(), name="dataset-version-list"),
    path("<uuid:dataset_pk>/versions/<uuid:pk>/", DatasetVersionDetailView.as_view(), name="dataset-version-detail"),
]
