import time
import os
import glob

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Polls dev_emails directory every 10 seconds and prints new emails to the terminal."

    def handle(self, *args, **options):
        email_dir = getattr(settings, "EMAIL_FILE_PATH", None)
        if not email_dir:
            self.stderr.write("EMAIL_FILE_PATH is not configured in settings.")
            return

        email_dir = str(email_dir)
        self.stdout.write(self.style.SUCCESS(f"Watching for new emails in: {email_dir}"))
        self.stdout.write("Press Ctrl+C to stop.\n")

        seen = set(glob.glob(os.path.join(email_dir, "*.log")))

        try:
            while True:
                time.sleep(10)
                current = set(glob.glob(os.path.join(email_dir, "*.log")))
                new_files = current - seen
                for filepath in sorted(new_files):
                    self.stdout.write("\n" + "=" * 72)
                    self.stdout.write(self.style.WARNING(f"📧  New email: {os.path.basename(filepath)}"))
                    self.stdout.write("=" * 72)
                    with open(filepath, encoding="utf-8") as f:
                        self.stdout.write(f.read())
                    self.stdout.write("=" * 72 + "\n")
                seen = current
        except KeyboardInterrupt:
            self.stdout.write("\nStopped watching for emails.")
