from django.urls import path
from .views import *

app_name = "core"

urlpatterns = [
    path("", ItemListView.as_view(), name="index"),
    path("item/<int:pk>/", ItemDetailView.as_view(), name="detail"),
    path("success/", success, name="success"),
    path("cancel/", cancel, name="cancel"),
    path("buy/<int:pk>/", CreateCheckoutSession.as_view(), name="create-checkout-single"),
    path("buy/", CreateCheckoutSession.as_view(), name="create-checkout-cart"),
    path("order/<int:pk>/", OrderView.as_view(), name="order_post"),
    path("order/", OrderView.as_view(), name="order_get"),
]