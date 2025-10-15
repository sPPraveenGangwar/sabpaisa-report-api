#!/usr/bin/env python3
"""
Script to check which fields actually exist in the database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from apps.transactions.models import TransactionDetail

def check_database_fields():
    """Check which fields exist in the actual database"""
    with connection.cursor() as cursor:
        # Get actual columns from database
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'transaction_detail'
            AND TABLE_SCHEMA = DATABASE()
        """)

        db_columns = [row[0] for row in cursor.fetchall()]

        print(f"Database has {len(db_columns)} columns")

        # Get model fields
        model_fields = [f.name for f in TransactionDetail._meta.get_fields()]
        print(f"Model has {len(model_fields)} fields")

        # Find mismatches
        missing_in_db = [f for f in model_fields if f not in db_columns]
        extra_in_db = [c for c in db_columns if c not in model_fields]

        if missing_in_db:
            print(f"\nFields in model but NOT in database ({len(missing_in_db)}):")
            for field in missing_in_db[:20]:  # Show first 20
                print(f"  - {field}")
            if len(missing_in_db) > 20:
                print(f"  ... and {len(missing_in_db) - 20} more")

        if extra_in_db:
            print(f"\nFields in database but NOT in model ({len(extra_in_db)}):")
            for field in extra_in_db[:20]:
                print(f"  - {field}")

        # Create safe fields list
        safe_fields = [f for f in model_fields if f in db_columns]
        print(f"\nSafe fields to use ({len(safe_fields)}):")
        print("SAFE_FIELDS = [")
        for i, field in enumerate(safe_fields):
            if i < len(safe_fields) - 1:
                print(f"    '{field}',")
            else:
                print(f"    '{field}'")
        print("]")

if __name__ == '__main__':
    try:
        check_database_fields()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()