from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

__all__ = [
    'User',
    'RedeemList',
    'MOPRedeem',
    'PaymentMethod',
    'Catogorie',
    'ACHRedeem',
    'Game',
    'DailyReport',
    'GameSummary',
    'RedeemGameList',
]


STATUS_CHOICES = (
    ("OF", "On File"),
    ("N", "New"),
)


class User(AbstractUser):
    pass

    class Meta:
        verbose_name_plural = "USERS"


class RedeemList(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.ForeignKey('PaymentMethod',
                                       on_delete=models.PROTECT,
                                       max_length=255,
                                       null=False, blank=False)
    category = models.ForeignKey('Catogorie',
                                 on_delete=models.PROTECT,
                                 max_length=255,
                                 blank=False, null=False,
                                 verbose_name='Category')
    send = models.FloatField(blank=True, null=True, verbose_name='Send')
    refund = models.FloatField(blank=True, null=True, verbose_name='Refund')
    mops_redeem = models.ForeignKey('MOPRedeem', blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "REDEEM LISTS"

    def clean(self):
        qs = RedeemList.objects.filter(mops_redeem=self.mops_redeem)
        refund_ls = qs.values_list("refund", flat=True)
        send_ls = qs.values_list("send", flat=True)

        refund_ls = [v if v else 0.0 for v in refund_ls]
        send_ls = [v if v else 0.0 for v in send_ls]
        # redeemed so far
        _sum = sum([sum(refund_ls), sum(send_ls)])

        extra = 0.0
        if self.id is None:
            # adding new item
            self.refund = self.refund if self.refund else 0.0
            self.send = self.send if self.send else 0.0
            extra = self.send+self.refund

        # updating an existing item with wrong redeem total
        redeem_itm = RedeemList.objects.filter(id=self.id).first()
        if redeem_itm:
            if self.refund != redeem_itm.refund:
                extra = self.refund - redeem_itm.refund
                if (_sum + extra) > self.mops_redeem.amount:
                    raise ValidationError('Send & Refund Amount cannot be larger than Redeem Amount')
            if self.send != redeem_itm.send:
                extra = self.send - redeem_itm.send
                if (_sum + extra) > self.mops_redeem.amount:
                    raise ValidationError('Send & Refund Amount cannot be larger than Redeem Amount')

        if (_sum + extra) > self.mops_redeem.amount:
            raise ValidationError('Send & Refund Amount cannot be larger than Redeem Amount')


class MOPRedeem(models.Model):
    customer = models.CharField(max_length=255, blank=False, null=False, verbose_name='Customer Name')
    amount = models.FloatField(blank=True, null=True, verbose_name='Redeem Amount', default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "MOP REDEEM"

    def __str__(self):
        return f"{self.customer} | ${self.amount}"

    @property
    def balance(self):
        qs = RedeemList.objects.filter(mops_redeem=self)
        refund_ls = qs.values_list("refund", flat=True)
        send_ls = qs.values_list("send", flat=True)

        refund_ls = [v if v else 0.0 for v in refund_ls]
        send_ls = [v if v else 0.0 for v in send_ls]
        # redeemed so far
        _sum = sum(refund_ls) + sum(send_ls)

        # if _sum >= self.amount:
        #     raise ValidationError('Send & Refund Amount cannot be larger than Redeem Amount')

        return self.amount - _sum


class PaymentMethod(models.Model):
    name = models.CharField(primary_key=True, max_length=255, blank=False, null=False)

    class Meta:
        verbose_name_plural = "PAYMENT METHODS"
        constraints = [
            models.UniqueConstraint(fields=['name'], name='payment method')
        ]

    def __str__(self): return self.name


class Catogorie(models.Model):
    name = models.CharField(primary_key=True, max_length=255, blank=False, null=False)

    class Meta:
        verbose_name_plural = "CATEGORIES"
        constraints = [
            models.UniqueConstraint(fields=['name'], name='cateogorie')
        ]

    def __str__(self): return self.name


class Transfer(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.CharField(max_length=255, blank=False, null=False, verbose_name='Customer Name')
    amount = models.FloatField(blank=True, null=True, verbose_name='Redeem Amount', default=0.0)
    from_game = models.ForeignKey('Game',
                                  on_delete=models.PROTECT,
                                  max_length=255,
                                  blank=False, null=False,
                                  verbose_name='From Game',
                                  related_name='_from_game')
    to_game = models.ForeignKey('Game',
                                on_delete=models.PROTECT,
                                max_length=255,
                                blank=False, null=False,
                                verbose_name='To Game',
                                related_name='_to_game')

    class Meta:
        verbose_name_plural = "TRANSFERS"

    def __str__(self): return self.customer

    def clean(self):
        if self.from_game == self.to_game:
            raise ValidationError('Transfers not possible between same games')


class ACHRedeem(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.CharField(max_length=255, blank=False, null=False, verbose_name='Customer Name')
    amount = models.FloatField(blank=True, null=True, verbose_name='Redeem Amount', default=0.0)
    on_file = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        verbose_name_plural = "ACH REDEEM"

    def __str__(self): return self.customer


class Game(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name_plural = "GAMES"
        constraints = [
            models.UniqueConstraint(fields=['name'], name='game')
        ]

    def __str__(self): return self.name


class DailyReport(models.Model):
    date = models.DateField(null=False, blank=False, unique=True)

    class Meta:
        verbose_name_plural = "DAILY REPORT"


class RedeemGameList(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    game = models.ForeignKey('Game',
                             on_delete=models.PROTECT,
                             max_length=255,
                             blank=False, null=False,
                             verbose_name='Game',
                             related_name='_game')
    amount = models.FloatField(blank=True, null=True, verbose_name='Amount', default=0.0)
    customer = models.CharField(max_length=255, blank=False, null=False, verbose_name='Customer Name')

    def __str__(self): return f"{self.customer}"
    class Meta:
        verbose_name_plural = "REDEEM LIST"

class GameSummary(models.Model):
    daily_report = models.ForeignKey('DailyReport',
                                     on_delete=models.PROTECT,
                                     max_length=255,
                                     blank=False, null=False,
                                     verbose_name='DailyReport',
                                     related_name='_daily_report')
    game = models.ForeignKey('Game',
                             on_delete=models.PROTECT,
                             max_length=255,
                             blank=False, null=False,
                             verbose_name='Game',
                             related_name='_gamesummary')
    system_in = models.FloatField(blank=True, null=True, verbose_name='In', default=0.0)
    system_out = models.FloatField(blank=True, null=True, verbose_name='Out', default=0.0)
    transfer = models.FloatField(blank=True, null=True, verbose_name='Transfer', default=0.0)
    cashout = models.FloatField(blank=True, null=True, verbose_name='Cashout', default=0.0)
