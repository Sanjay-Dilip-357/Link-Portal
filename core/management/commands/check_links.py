# core/management/commands/check_links.py
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Link


class Command(BaseCommand):
    help = 'Check all links for broken URLs'

    def add_arguments(self, parser):
        parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')

    def handle(self, *args, **options):
        timeout = options['timeout']
        links = Link.objects.filter(is_active=True)
        total = links.count()
        broken = 0
        active = 0

        self.stdout.write(f'Checking {total} links...')

        for link in links:
            try:
                response = requests.head(link.url, timeout=timeout, allow_redirects=True)
                if response.status_code < 400:
                    link.link_status = 'active'
                    active += 1
                else:
                    link.link_status = 'broken'
                    broken += 1
                    self.stdout.write(self.style.WARNING(f'BROKEN: {link.title} - {link.url} (Status: {response.status_code})'))
            except requests.RequestException as e:
                link.link_status = 'broken'
                broken += 1
                self.stdout.write(self.style.ERROR(f'ERROR: {link.title} - {link.url} ({str(e)})'))

            link.last_checked = timezone.now()
            link.save(update_fields=['link_status', 'last_checked'])

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Active: {active}, Broken: {broken}, Total: {total}'
        ))