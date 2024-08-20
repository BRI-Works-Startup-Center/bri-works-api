from django.urls import path, re_path
from .views import TenantAPI, TenantCatalogAPI, OrderAPI, OrderDetailAPI, OrderHistoryAPI

urlpatterns = [
  path("", TenantAPI.as_view()),
  path("<uuid:tenant_id>", TenantCatalogAPI.as_view()),
  path("order/<uuid:order_id>", OrderDetailAPI.as_view()),
  path("order", OrderAPI.as_view()),
  path("order/history", OrderHistoryAPI.as_view()),
]