import csv
from datetime import datetime
from functools import partial

from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models.aggregates import Sum
from django.db.models.query_utils import Q
from django.http.response import HttpResponse
from django.utils.html import format_html
from rangefilter.filters import DateRangeFilterBuilder

from data.filters import CategoryListFilter, PaymentMethodListFilter, CatogorieListFilter, PaymentListFilter, \
    CustomerListFilter, BaseCatogorieListFilter, BasePaymentListFilter
from data.forms import RedeemListForm, TransferAdminForm, GameReportForm, GameForm
from data.models import (MOPRedeem, PaymentMethod, Catogorie, User, Transfer, ACHRedeem, Game, RedeemList, GameSummary)
from django.contrib.auth.admin import UserAdmin


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class StaffUserAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return True

    def has_change_permission(self, request, obj=None): return True

    def has_delete_permission(self, request, obj=None): return True

    def has_module_permission(self, request): return True
class RedeemListInline(admin.TabularInline):
    model = RedeemList
    form = RedeemListForm
    extra = 1
@admin.register(RedeemList)
class Reporting(admin.ModelAdmin):
    change_list_template = 'admin/data/redeemlist/change_list.html'
    model = RedeemList
    list_filter = [
        ('created_at', DateRangeFilterBuilder()),
        BaseCatogorieListFilter,
        BasePaymentListFilter,
        CustomerListFilter,
    ]
    list_display = ("customer", "created_at", "category", "payment_method", "refund", "send", "grand_total", )

    def customer(self, obj): return obj.mops_redeem.customer

    def created_at(self, obj): return obj.mops_redeem.created_at.date()

    def grand_total(self, obj): return obj.refund + obj.send

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['refund'] = sum([item.refund for item in self.get_queryset(request)])
        extra_context['send'] = sum([item.send for item in self.get_queryset(request)])
        extra_context['grand_total'] = extra_context['refund'] + extra_context['send']
        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        filters = Q()
        # following is a fix for the created_at field in the RedeemList
        if 'created_at__range__gte' in request.GET:
            date = datetime.strptime(request.GET.get('created_at__range__gte'), '%Y-%m-%d')
            filters &= Q(created_at__date__gte=date)
        if 'created_at__range__lte' in request.GET:
            date = datetime.strptime(request.GET.get('created_at__range__lte'), '%Y-%m-%d')
            filters &= Q(created_at__date__lte=date)

        payment_methods = request.GET.get('payment_method')
        pm = None
        if payment_methods:
            pm = payment_methods.split(',')

        category = request.GET.get('category')
        c = None
        if category:
            c = category.split(',')

        if c and pm:
            filters &= Q(payment_method__in=pm, category__in=c)
        if c:
            filters &= Q(category__in=c)
        if pm:
            filters &= Q(payment_method__in=pm)

        return qs.filter(filters)


@admin.register(MOPRedeem)
class MOPsRedeemAdmin(StaffUserAdmin, ExportCsvMixin):
    change_list_template = 'admin/data/mopredeem/change_list.html'
    list_filter = [
        ('created_at', DateRangeFilterBuilder()),
        CatogorieListFilter,
        PaymentListFilter,
        "customer",
    ]
    list_display = ("customer", "amount", "created_at", "export_screenshot")
    readonly_fields = ('balance',)
    inlines = [
        RedeemListInline,
    ]
    actions = ['export_selected_as_csv']

    def export_selected_as_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=mops_redeem_data.csv'
        writer = csv.writer(response)
        writer.writerow(['Customer', 'Amount', 'Created At'])
        for mop_redeem in queryset:
            writer.writerow([
                mop_redeem.customer,
                mop_redeem.amount,
                mop_redeem.created_at,
            ])

        return response
    export_selected_as_csv.short_description = "Export selected MOPs Redeem as CSV"

    def export_screenshot(self, obj):
        html = '<input type="button" onclick="location.href=\'{}\'" value="Export JPG"/>'.format(f"/export-jpg?id={obj.id}")
        return format_html(html)

    def balance(self, obj):
        return obj.balance

    @admin.display(description='Customer')
    def my_customer(self, obj): return obj.customer

    @admin.display(description='Amount')
    def my_amount(self, obj): return obj.amount

    @admin.display(description='Payment Method')
    def my_payment_method(self, obj): return obj.payment_method

    @admin.display(description='Category')
    def my_category(self, obj): return obj.category

    @admin.display(description='Created Date')
    def my_created_at(self, obj): return obj.created_at.date()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # we should not do get('payment_method', ''), this is not good code practice

        qs = RedeemList.objects.filter(mops_redeem_id__in=self.get_queryset(request).values_list('id', flat=True))

        extra_context['refund'] = sum([item.refund for item in qs])
        extra_context['send'] = sum([item.send for item in qs])
        extra_context['grand_total'] = extra_context['refund'] + extra_context['send']
        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        qs = super(MOPsRedeemAdmin, self).get_queryset(request)
        filters = Q()

        # following is a fix for the created_at field in the RedeemList
        if 'created_at__range__gte' in request.GET:
            date = datetime.strptime(request.GET.get('created_at__range__gte'), '%Y-%m-%d')
            filters &= Q(created_at__date__gte=date)
        if 'created_at__range__lte' in request.GET:
            date = datetime.strptime(request.GET.get('created_at__range__lte'), '%Y-%m-%d')
            filters &= Q(created_at__date__lte=date)

        payment_methods = request.GET.get('payment_method')
        pm = None
        if payment_methods:
            pm = payment_methods.split(',')

        category = request.GET.get('category')
        c = None
        if category:
            c = category.split(',')

        if c and pm:
            filters &= Q(payment_method__in=pm, category__in=c)
        if c:
            filters &= Q(category__in=c)
        if pm:
            filters &= Q(payment_method__in=pm)

        ls = list(RedeemList.objects.filter(filters).values_list('mops_redeem', flat=True).distinct())
        return qs.filter(amount__gt=0.0, id__in=ls)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super(MOPsRedeemAdmin, self).get_form(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name != "redeem_list":
            kwargs.pop('obj', None)
        return super(MOPsRedeemAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        mops_redeem = kwargs.pop('obj', None)

        if db_field.name == 'redeem_list' and mops_redeem:
            kwargs["queryset"] = MOPRedeem.objects\
                .filter(customer=mops_redeem.customer, created_at__date=str(mops_redeem.created_at.date()))
        else:
            kwargs["queryset"] = MOPRedeem.objects.none()
        return super(MOPsRedeemAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)



# @admin.register(RedeemGameList)
# class RedeemGameListAdmin(admin.ModelAdmin):
#     list_display = ('customer', 'created_at', )


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('customer', 'created_at', )
    form = TransferAdminForm


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', )
    form = GameForm


class GameReportInline(admin.TabularInline):
    model = GameSummary
    form = GameReportForm
    extra = 0
    fields = ('game', 'system_in', 'system_out', 'transfer', 'cashout', )

    def has_change_permission(self, request, obj=None):
        return False


# @admin.register(DailyReport)
# class DailyReportAdmin(admin.ModelAdmin):
#     list_filter = [
#         "date"
#     ]
#     list_display = ("date", )
#     readonly_fields = ('date',)
#     inlines = [
#         GameReportInline,
#     ]


admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(PaymentMethod)
admin.site.register(Catogorie)
admin.site.register(ACHRedeem)
