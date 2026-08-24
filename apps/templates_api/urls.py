from django.urls import path

from .views import IndustryTemplateListView

urlpatterns = [
    path("", IndustryTemplateListView.as_view(), name="template-list"),
]
