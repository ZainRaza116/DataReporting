import os
import numpy as np

from dal import autocomplete
from django.http.response import HttpResponse
from django.views.generic.base import View

from DataReportingApp import settings
from data.models import (PaymentMethod, Catogorie, RedeemList, MOPRedeem)


class PaymentMethodView(autocomplete.Select2ListView):

    def get_list(self):
        if not self.request.user.is_authenticated:
            return []
        return PaymentMethod.objects.values_list("name", flat=True)


class CategoryView(autocomplete.Select2ListView):

    def get_list(self):
        if not self.request.user.is_authenticated:
            return []
        return Catogorie.objects.values_list("name", flat=True)


class ExportJPEGView(View):

    def get(self, request):
        _id = request.GET.get('id')
        qs = RedeemList.objects.filter(mops_redeem=_id).values_list('payment_method',
                                                                    'category',
                                                                    'send',
                                                                    'refund')
        mops_obj = MOPRedeem.objects.filter(id=_id).first()
        if mops_obj:
            file_name = f"{settings.MEDIA_ROOT}{mops_obj.customer}_{mops_obj.created_at}.csv"
        else:
            file_name = f"{settings.MEDIA_ROOT}mops_redeem.csv"
        ls = list(qs)
        for idx, i in enumerate(list(ls)):
            ls[idx] = list(ls[idx])
            ls[idx][2] = int(ls[idx][2])
            ls[idx][3] = int(ls[idx][3])

        my_data = np.array(ls)
        my_data[:, 2:] = my_data[:, 2:].astype(np.int64)
        np.savetxt(file_name, my_data, fmt='%s', delimiter=',', header='payment_method,category,send,refund')

        content = open(file_name, 'r').read()
        response = HttpResponse(content, content_type='text/csv')
        response['Content-Length'] = os.path.getsize(file_name)
        response['Content-Disposition'] = 'attachment; filename=%s' % file_name

        return response
