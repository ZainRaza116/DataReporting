from django.urls import path

from data.views import (PaymentMethodView, CategoryView, ExportJPEGView)

urlpatterns = [
    path("payment_method", PaymentMethodView.as_view(), name='payment_method'),
    path("categories", CategoryView.as_view(), name='categories'),
    path("export-jpg", ExportJPEGView.as_view(), name='export-jpg'),
]
