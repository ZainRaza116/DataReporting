from datetime import date

from django.contrib import admin
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _
from django_admin_multiple_choice_list_filter.list_filters import MultipleChoiceListFilter

from data.models import Catogorie, RedeemList, PaymentMethod, MOPRedeem


class CategoryListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Category")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "category"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        return [
            (obj.name, obj.name) for obj in Catogorie.objects.all()
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not self.value():
            return queryset

        qs = RedeemList.objects.filter(category__name=self.value())
        return queryset.filter(id__in=[q.mops_redeem.id for q in qs])


class PaymentMethodListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _("Payment Method")

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "payment_method"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """

        return [
            (obj.name, obj.name) for obj in PaymentMethod.objects.all()
        ]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if not self.value():
            return queryset

        qs = RedeemList.objects.filter(payment_method__name=self.value())
        return queryset.filter(id__in=[q.mops_redeem.id for q in qs])


class BaseCatogorieListFilter(MultipleChoiceListFilter):
    title = 'Catogorie'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return list(map(lambda x: (x, x), Catogorie.objects.all().values_list('name', flat=True)))

    def queryset(self, request, queryset):
        if request.GET.get(self.parameter_name):
            kwargs = {f"{self.parameter_name}__in": request.GET[self.parameter_name].split(',')}
            queryset = queryset.filter(Q(**kwargs))
        return queryset


class CatogorieListFilter(BaseCatogorieListFilter):
    def queryset(self, request, queryset):
        if request.GET.get(self.parameter_name):
            kwargs = {f"{self.parameter_name}__in": request.GET[self.parameter_name].split(',')}
            ls = RedeemList.objects.filter(Q(**kwargs)).values_list('mops_redeem', flat=True).distinct()
            return MOPRedeem.objects.filter(id__in=(list(ls)))
        return queryset


class BasePaymentListFilter(MultipleChoiceListFilter):
    title = 'Payment'
    parameter_name = 'payment_method'

    def lookups(self, request, model_admin):
        return list(map(lambda x: (x, x), PaymentMethod.objects.all().values_list('name', flat=True)))

    def queryset(self, request, queryset):
        if request.GET.get(self.parameter_name):
            kwargs = {f"{self.parameter_name}__in": request.GET[self.parameter_name].split(',')}
            queryset = queryset.filter(Q(**kwargs))
        return queryset


class PaymentListFilter(BasePaymentListFilter):
    def queryset(self, request, queryset):
        if request.GET.get(self.parameter_name):
            kwargs = {f"{self.parameter_name}__in": request.GET[self.parameter_name].split(',')}
            ls = RedeemList.objects.filter(Q(**kwargs)).values_list('mops_redeem', flat=True).distinct()
            return MOPRedeem.objects.filter(id__in=(list(ls)))
        return queryset


class CustomerListFilter(MultipleChoiceListFilter):
    title = 'Customer'
    parameter_name = 'customer'

    def lookups(self, request, model_admin):
        return list(map(lambda x: (x, x), MOPRedeem.objects.all().values_list('customer', flat=True).distinct()))

    def queryset(self, request, queryset):
        if request.GET.get(self.parameter_name):
            if self.parameter_name == 'customer':
                kwargs = {f"mops_redeem__{self.parameter_name}__in": request.GET[self.parameter_name].split(',')}
            else:
                kwargs = {f"{self.parameter_name}__in": request.GET[self.parameter_name].split(',')}
            queryset = queryset.filter(Q(**kwargs))
        return queryset
