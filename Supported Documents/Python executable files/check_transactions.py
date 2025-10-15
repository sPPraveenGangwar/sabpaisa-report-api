import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta, datetime
from apps.transactions.models import TransactionDetail

# Get today's date
today_end = timezone.now()
today_start = today_end.replace(hour=0, minute=0, second=0, microsecond=0)

print("="*50)
print("TRANSACTION COUNT ANALYSIS")
print("="*50)
print(f"Current time: {today_end}")
print(f"Today start: {today_start}")
print(f"Today end: {today_end}")
print()

# Total count in database
total_count = TransactionDetail.objects.count()
print(f"Total transactions in database: {total_count}")

# Count with trans_date = today (exact date match)
today_date = datetime.now().date()
exact_today = TransactionDetail.objects.filter(trans_date__date=today_date).count()
print(f"Transactions with trans_date on {today_date}: {exact_today}")

# Count with date range filter (what API uses)
filtered_count = TransactionDetail.objects.filter(
    trans_date__gte=today_start,
    trans_date__lte=today_end
).count()
print(f"Transactions filtered by date range (API logic): {filtered_count}")

# Count with NULL trans_date
null_count = TransactionDetail.objects.filter(trans_date__isnull=True).count()
print(f"Transactions with NULL trans_date: {null_count}")

# Count transactions outside today's range
outside_range = TransactionDetail.objects.filter(
    trans_date__lt=today_start
).count() + TransactionDetail.objects.filter(
    trans_date__gt=today_end
).count()
print(f"Transactions outside today's range: {outside_range}")

print()
print("Sample of excluded transactions:")
excluded = TransactionDetail.objects.exclude(
    trans_date__gte=today_start,
    trans_date__lte=today_end
)[:5].values('txn_id', 'trans_date', 'status')

for txn in excluded:
    print(f"  - ID: {txn['txn_id']}, Date: {txn['trans_date']}, Status: {txn['status']}")
