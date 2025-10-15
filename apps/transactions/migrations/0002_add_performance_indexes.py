# Generated migration for adding performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0001_initial'),
    ]

    operations = [
        # Add index on trans_date for faster date range queries
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS idx_transaction_trans_date
            ON sabpaisa_txn_details (trans_date);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_transaction_trans_date ON sabpaisa_txn_details;"
        ),

        # Add composite index on status and trans_date for SUCCESS transaction queries
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS idx_transaction_status_date
            ON sabpaisa_txn_details (status, trans_date);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_transaction_status_date ON sabpaisa_txn_details;"
        ),

        # Add index on client_code for merchant filtering
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS idx_transaction_client_code
            ON sabpaisa_txn_details (client_code);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_transaction_client_code ON sabpaisa_txn_details;"
        ),

        # Add index on payment_mode for payment analytics
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS idx_transaction_payment_mode
            ON sabpaisa_txn_details (payment_mode);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_transaction_payment_mode ON sabpaisa_txn_details;"
        ),

        # Add composite index for settlement queries
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS idx_transaction_settlement
            ON sabpaisa_txn_details (is_settled, status, trans_date);
            """,
            reverse_sql="DROP INDEX IF EXISTS idx_transaction_settlement ON sabpaisa_txn_details;"
        ),
    ]
