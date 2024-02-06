from django import forms
from django.core.exceptions import ValidationError

from data.models import (PaymentMethod, Catogorie, RedeemList, Transfer, Game, GameSummary)


class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        if self._name == 'category':
            value = Catogorie.objects.filter(name=value).first()
            if value is not None:
                value = value.name
        if self._name == 'payment_method':
            value = PaymentMethod.objects.filter(name=value).first()
            if value is not None:
                value = value.name

        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return (text_html + data_list)


class RedeemListForm(forms.ModelForm):
    payment_method = forms.CharField(required=True)
    category = forms.CharField(required=True)
    send = forms.FloatField(required=False)
    refund = forms.FloatField(required=False)

    def __init__(self, *args, **kwargs):
        _payment_method_list = list(PaymentMethod.objects.all().values_list("name", flat=True))
        _category_list = list(Catogorie.objects.all().values_list("name", flat=True))
        super(RedeemListForm, self).__init__(*args, **kwargs)

        # the "name" parameter will allow you to use the same widget more than once in the same
        # form, not setting this parameter differently will cuse all inputs display the
        # same list.
        self.fields['payment_method'].widget = ListTextWidget(data_list=_payment_method_list, name='payment_method')
        self.fields['category'].widget = ListTextWidget(data_list=_category_list, name='category')

    def clean_payment_method(self):
        try:
            data = PaymentMethod.objects.get(name=self.cleaned_data['payment_method'])
        except PaymentMethod.DoesNotExist:
            raise ValidationError('This Payment Method does not exist!')

        return data

    def clean_category(self):
        try:
            data = Catogorie.objects.get(name=self.cleaned_data['category'])
        except Catogorie.DoesNotExist:
            raise ValidationError('This Category does not exist!')

        return data

    class Meta:
        model = RedeemList
        fields = ['payment_method', 'category', 'send', 'refund']


class GameReportForm(forms.ModelForm):
    class Meta:
        model = GameSummary
        fields = (
            'game',
            'system_in',
            'system_out',
            'transfer',
            'cashout',
        )


class TransferAdminForm(forms.ModelForm):

    class Meta:
        model = Transfer
        fields = ('customer', 'amount', 'from_game', 'to_game', )


class GameForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = ('name', )
