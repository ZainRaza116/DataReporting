from datetime import datetime

from django.core.management.base import BaseCommand

from data.models import Transfer, Game, DailyReport, GameSummary, RedeemGameList


class Command(BaseCommand):

    def handle(self, *args, **options):
        today = datetime.now().date()
        daily_report, created = DailyReport.objects.get_or_create(date=today)

        for game in Game.objects.all():
            system_out = sum(Transfer.objects.filter(from_game=game,
                                                     created_at__date=today).values_list("amount", flat=True))
            system_in = sum(Transfer.objects.filter(to_game=game,
                                                    created_at__date=today).values_list("amount", flat=True))
            transfer = sum(RedeemGameList.objects.filter(game=game,
                                                         created_at__date=today).values_list("amount", flat=True))
            GameSummary.objects.get_or_create(
                daily_report=daily_report,
                game=game,
                system_in=system_in,
                system_out=system_out,
                transfer=transfer,
                cashout=system_out-transfer,
            )
